import os
import json
import glob
import re
import time
from datetime import datetime
from pathlib import Path
import paho.mqtt.client as mqtt
import requests
import PyPDF2
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DocumentProcessor")

class DocumentProcessor:
    def __init__(self):
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.mistral_url = os.getenv("MISTRAL_BASE_URL", "http://localhost:11434")
        self.upload_dir = "/app/uploads"
        self.doc_dir = "/app/documents"
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected")
        else:
            logger.error(f"MQTT connection failed: {rc}")

    def extract_text_from_pdf(self, pdf_path):
        """Extract text from PDF document"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text()
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
        return text

    def extract_vessel_data_with_mistral(self, text, doc_name):
        """Use Mistral to extract structured vessel data from document"""
        try:
            prompt = f"""Extract vessel and maritime incident information from this document. 
            Return JSON with:
            - mmsi: Maritime Mobile Service Identity (if available)
            - name: Vessel name
            - type: Vessel type (cargo, tanker, fishing, military, etc.)
            - description: Physical description
            - last_known_position: Coordinates (lat, long)
            - coordinates: {{"lat": X, "lon": Y}}
            - search_radius: Search radius in nautical miles
            - alert_type: MAYDAY, SINKING, FIRE, COLLISION, OIL_SPILL, MISSING_CREW, etc.
            - status: Current status
            - crew_count: Number of crew
            - cargo: Cargo description
            - timestamp: Event timestamp
            
            Document:
            {text[:3000]}
            """
            
            response = requests.post(
                f"{self.mistral_url}/api/generate",
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted = self._parse_vessel_json(result.get("response", ""))
                return extracted
        except Exception as e:
            logger.error(f"Error with Mistral extraction: {e}")
        
        # Fallback: regex extraction
        return self._extract_vessel_regex(text)

    def _parse_vessel_json(self, response_text):
        """Parse JSON from Mistral response"""
        try:
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            else:
                json_str = response_text
            return json.loads(json_str)
        except:
            return {}

    def _extract_vessel_regex(self, text):
        """Fallback regex-based extraction"""
        data = {}
        
        # Extract coordinates
        coord_patterns = [
            r"(\d+\.?\d*)[°\s]*([NS])\s*(\d+\.?\d*)[°\s]*([EW])",
            r"Lat(?:itude)?:?\s*(\d+\.?\d*)\s*Lon(?:gitude)?:?\s*(\d+\.?\d*)",
        ]
        
        for pattern in coord_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                data["coordinates"] = {"lat": float(match.group(1)), "lon": float(match.group(3))}
                break
        
        # Extract vessel name
        name_match = re.search(r"(?:vessel|ship|boat).*?name:?\s*([^\n]+)", text, re.IGNORECASE)
        if name_match:
            data["name"] = name_match.group(1).strip()
        
        # Extract MMSI
        mmsi_match = re.search(r"MMSI:?\s*(\d{9})", text)
        if mmsi_match:
            data["mmsi"] = mmsi_match.group(1)
        
        # Extract alert type
        alert_keywords = ["MAYDAY", "SINKING", "FIRE", "COLLISION", "OIL_SPILL"]
        for keyword in alert_keywords:
            if keyword.lower() in text.lower():
                data["alert_type"] = keyword
                break
        
        return data

    def process_uploaded_documents(self):
        """Monitor upload directory for new documents"""
        processed_docs = set()
        
        while True:
            try:
                pdf_files = glob.glob(f"{self.upload_dir}/*.pdf")
                
                for pdf_path in pdf_files:
                    if pdf_path not in processed_docs:
                        logger.info(f"Processing document: {pdf_path}")
                        
                        # Extract text
                        text = self.extract_text_from_pdf(pdf_path)
                        
                        if text:
                            # Extract structured vessel data
                            vessel_data = self.extract_vessel_data_with_mistral(
                                text,
                                Path(pdf_path).name
                            )
                            
                            # Add metadata
                            vessel_data["source_document"] = Path(pdf_path).name
                            vessel_data["processed_at"] = datetime.now().isoformat()
                            
                            # Save to documents directory
                            output_file = f"{self.doc_dir}/{Path(pdf_path).stem}_extracted.json"
                            with open(output_file, 'w') as f:
                                json.dump(vessel_data, f, indent=2)
                            
                            logger.info(f"Extracted vessel data: {vessel_data.get('name', 'Unknown')}")
                            
                            # Publish to MQTT for CV agent to register
                            self.mqtt_client.publish(
                                "maritime/documents/processed",
                                json.dumps(vessel_data),
                                qos=1
                            )
                        
                        processed_docs.add(pdf_path)
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Error processing documents: {e}")
                time.sleep(5)

    def run(self):
        """Start document processor"""
        logger.info("Starting Document Processor...")
        
        # Ensure directories exist
        Path(self.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(self.doc_dir).mkdir(parents=True, exist_ok=True)
        
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_start()
        
        try:
            self.process_uploaded_documents()
        except KeyboardInterrupt:
            logger.info("Shutting down Document Processor")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.run()
