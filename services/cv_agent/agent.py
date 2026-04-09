import os
import json
import base64
import glob
import time
from datetime import datetime
from pathlib import Path
import paho.mqtt.client as mqtt
import requests
from PIL import Image
import io
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CVAgent")

# Maritime threat categories
THREAT_CLASSES = {
    "smuggling_vessel": {"keywords": ["small boat", "covered cargo", "night operation"], "severity": 0.8},
    "wreck": {"keywords": ["sunken", "debris", "capsized"], "severity": 0.9},
    "oil_spill": {"keywords": ["slick", "discoloration", "pollution"], "severity": 0.85},
    "vessel_gathering": {"keywords": ["multiple boats", "clustered", "rendezvous"], "severity": 0.7},
    "weapons": {"keywords": ["gun", "mounted weapon", "military hardware"], "severity": 0.95},
    "military_vessel": {"keywords": ["warship", "naval", "military markings"], "severity": 0.6},
    "pirates": {"keywords": ["armed boarding", "hostile approach"], "severity": 0.95},
    "dark_vessel": {"keywords": ["no lights", "unlit", "dark"], "severity": 0.75},
    "fire": {"keywords": ["flames", "smoke", "burning"], "severity": 0.9},
    "endangered_waters": {"keywords": ["prohibited zone", "restricted area"], "severity": 0.8},
}

class MaritimeCVAgent:
    def __init__(self):
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.mistral_url = os.getenv("MISTRAL_BASE_URL", "http://localhost:11434")
        self.frame_dir = os.getenv("FRAME_INPUT_DIR", "/app/frames")
        self.doc_dir = os.getenv("DOCUMENTS", "/app/documents")
        self.threshold = float(os.getenv("THREAT_CONFIDENCE_THRESHOLD", 0.6))
        self.enable_correlation = os.getenv("CORRELATION_ENABLED", "true").lower() == "true"
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.vessel_registry = {}  # Matches PDF vessel data to video
        self.detection_history = {}
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected")
            self.mqtt_client.subscribe("maritime/frames/new")
            self.mqtt_client.subscribe("maritime/documents/processed")
        else:
            logger.error(f"MQTT connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            if msg.topic == "maritime/documents/processed":
                payload = json.loads(msg.payload.decode())
                self._handle_vessel_data(payload)
        except Exception as e:
            logger.error(f"Error handling MQTT message: {e}")

    def _handle_vessel_data(self, vessel_data):
        """Store vessel info from processed documents for correlation"""
        vessel_key = f"{vessel_data.get('mmsi')}_{vessel_data.get('name')}"
        self.vessel_registry[vessel_key] = {
            "mmsi": vessel_data.get("mmsi"),
            "name": vessel_data.get("name"),
            "description": vessel_data.get("description"),
            "coordinates": vessel_data.get("coordinates"),
            "radius": vessel_data.get("search_radius", 5),
            "alert_type": vessel_data.get("alert_type", "MAYDAY"),
            "timestamp": datetime.now().isoformat(),
        }
        logger.info(f"Registered vessel for correlation: {vessel_key}")

    def analyze_frame_with_mistral(self, frame_path):
        """Send frame to Mistral vision model for threat analysis"""
        try:
            with open(frame_path, "rb") as img_file:
                img_data = base64.b64encode(img_file.read()).decode("utf-8")
            
            # Build prompt for maritime threat detection
            prompt = self._build_threat_detection_prompt()
            
            response = requests.post(
                f"{self.mistral_url}/api/generate",
                json={
                    "model": "llava",  # or bakllava for maritime domain
                    "prompt": prompt,
                    "images": [img_data],
                    "stream": False,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._parse_threat_response(result.get("response", ""))
            else:
                logger.error(f"Mistral API error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error analyzing frame: {e}")
            return None

    def _build_threat_detection_prompt(self):
        """Build comprehensive maritime threat detection prompt"""
        return """Analyze this maritime scene for illegal or suspicious activities.

        Check for:
        1. SMUGGLING VESSELS: Small boats, covered cargo, night operations
        2. WRECKS/DEBRIS: Sunken vessels, floating debris, capsized boats
        3. OIL SPILLS: Surface discoloration, pollution slicks
        4. VESSEL GATHERINGS: Multiple boats in close proximity, rendezvous
        5. WEAPONS: Mounted guns, military hardware
        6. MILITARY VESSELS: Warships, naval vessels, military markings
        7. PIRATES: Armed boarding, hostile approach vectors
        8. DARK VESSELS: Unlit boats at night, no navigation lights
        9. FIRES: Active flames, heavy smoke, burning wreckage
        10. ENDANGERED WATERS: Proximity to restricted zones, shallow waters

        For each threat detected, provide:
        - Threat Type
        - Confidence (0.0-1.0)
        - Location in frame (quadrant)
        - Description
        - Recommended action

        Format as JSON array of threats."""

    def _parse_threat_response(self, response_text):
        """Extract threat data from Mistral response"""
        threats = []
        try:
            # Try to extract JSON from response
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            else:
                json_str = response_text
            
            parsed = json.loads(json_str)
            threats = parsed if isinstance(parsed, list) else [parsed]
            
            # Filter by confidence threshold
            threats = [t for t in threats if t.get("confidence", 0) >= self.threshold]
            
        except json.JSONDecodeError:
            logger.warning("Could not parse Mistral JSON response")
        
        return threats

    def correlate_with_vessel_registry(self, threats, frame_path):
        """Match detected threats with registered vessels from documents"""
        if not self.enable_correlation or not threats:
            return threats
        
        for threat in threats:
            for vessel_key, vessel_data in self.vessel_registry.items():
                # Simple correlation: check if description matches threat location/type
                vessel_desc = vessel_data.get("description", "").lower()
                threat_desc = threat.get("description", "").lower()
                
                # If threat matches vessel characteristics or area
                if any(word in threat_desc for word in vessel_desc.split()):
                    threat["correlated_vessel"] = {
                        "name": vessel_data["name"],
                        "mmsi": vessel_data["mmsi"],
                        "alert_type": vessel_data["alert_type"],
                        "vessel_coords": vessel_data["coordinates"],
                    }
                    threat["correlation_confidence"] = 0.85
                    threat["severity"] = "CRITICAL"
                    logger.info(f"CORRELATION: Threat matched to vessel {vessel_key}")
        
        return threats

    def generate_sitrep(self, threats, frame_path, frame_timestamp):
        """Generate tactical situation report"""
        sitrep = {
            "timestamp": frame_timestamp,
            "frame": frame_path,
            "threat_count": len(threats),
            "threats": threats,
            "overall_threat_level": self._calculate_threat_level(threats),
            "commander_report": self._generate_commander_report(threats),
            "recommended_actions": self._generate_actions(threats),
        }
        return sitrep

    def _calculate_threat_level(self, threats):
        """Calculate overall threat level"""
        if not threats:
            return "GREEN"
        max_severity = max([t.get("confidence", 0) for t in threats], default=0)
        if max_severity >= 0.9:
            return "RED"
        elif max_severity >= 0.75:
            return "YELLOW"
        else:
            return "ORANGE"

    def _generate_commander_report(self, threats):
        """Generate natural language commander's report"""
        if not threats:
            return "No threats detected. All clear."
        
        report = f"MARITIME THREAT REPORT - {len(threats)} threat(s) identified:\n"
        for i, threat in enumerate(threats, 1):
            report += f"\n{i}. {threat.get('threat_type', 'UNKNOWN').upper()}\n"
            report += f"   Confidence: {threat.get('confidence', 0):.1%}\n"
            report += f"   Location: {threat.get('location', 'Unknown')}\n"
            report += f"   Details: {threat.get('description', 'N/A')}\n"
            if "correlated_vessel" in threat:
                report += f"   → CORRELATED WITH VESSEL: {threat['correlated_vessel']['name']}\n"
                report += f"   → ALERT TYPE: {threat['correlated_vessel']['alert_type']}\n"
        
        return report

    def _generate_actions(self, threats):
        """Generate recommended actions"""
        actions = []
        for threat in threats:
            threat_type = threat.get("threat_type", "").lower()
            if "weapon" in threat_type or "pirate" in threat_type:
                actions.append("ESCALATE to command, scramble response vessel")
            elif "wreck" in threat_type or "oil_spill" in threat_type:
                actions.append("Alert coastal authority, dispatch recovery team")
            elif "fire" in threat_type:
                actions.append("Dispatch emergency services, request fire suppression")
            elif "correlated_vessel" in threat:
                actions.append("PRIORITY: Intercept and investigate vessel")
        
        return actions

    def publish_alert(self, sitrep, frame_path):
        """Publish MQTT alert with thumbnail and report"""
        try:
            # Encode frame as base64 thumbnail
            img = Image.open(frame_path)
            img.thumbnail((640, 480))
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            thumbnail_b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            
            alert = {
                "timestamp": datetime.now().isoformat(),
                "threat_level": sitrep["overall_threat_level"],
                "threat_count": sitrep["threat_count"],
                "thumbnail": thumbnail_b64,
                "sitrep": sitrep["commander_report"],
                "threats": sitrep["threats"],
                "recommended_actions": sitrep["recommended_actions"],
            }
            
            # Publish to appropriate severity topic
            severity = sitrep["overall_threat_level"]
            topic = f"maritime/threats/{severity.lower()}"
            
            self.mqtt_client.publish(
                topic,
                json.dumps(alert),
                qos=2 if severity == "RED" else 1
            )
            
            logger.info(f"Published threat alert: {severity}")
            
        except Exception as e:
            logger.error(f"Error publishing alert: {e}")

    def process_frame_queue(self):
        """Continuously process new frames from ingestion service"""
        processed_frames = set()
        
        while True:
            try:
                frame_files = glob.glob(f"{self.frame_dir}/*.jpg") + glob.glob(f"{self.frame_dir}/*.png")
                
                for frame_path in frame_files:
                    if frame_path not in processed_frames:
                        logger.info(f"Analyzing frame: {frame_path}")
                        
                        # Run threat detection
                        threats = self.analyze_frame_with_mistral(frame_path)
                        
                        if threats:
                            # Correlate with vessel registry
                            threats = self.correlate_with_vessel_registry(threats, frame_path)
                            
                            # Generate SITREP
                            sitrep = self.generate_sitrep(
                                threats,
                                frame_path,
                                datetime.now().isoformat()
                            )
                            
                            # Publish alert
                            self.publish_alert(sitrep, frame_path)
                            
                            # Save detection to history
                            self.detection_history[frame_path] = sitrep
                        
                        processed_frames.add(frame_path)
                
                time.sleep(2)  # Check for new frames every 2 seconds
                
            except Exception as e:
                logger.error(f"Error in frame processing loop: {e}")
                time.sleep(5)

    def run(self):
        """Start CV agent"""
        logger.info("Starting Maritime CV Agent...")
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_start()
        
        try:
            self.process_frame_queue()
        except KeyboardInterrupt:
            logger.info("Shutting down CV Agent")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


if __name__ == "__main__":
    agent = MaritimeCVAgent()
    agent.run()
