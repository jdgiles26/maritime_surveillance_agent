import os
import json
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
import paho.mqtt.client as mqtt
import requests
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlertDispatcher")

class AlertDispatcher:
    def __init__(self):
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.slack_webhook = os.getenv("SLACK_WEBHOOK_URL", "")
        self.email_from = os.getenv("EMAIL_FROM", "")
        self.email_to = os.getenv("EMAIL_TO", "").split(",")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.smtp_user = os.getenv("SMTP_USER", self.email_from)
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        
    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected")
            # Subscribe to all threat levels
            self.mqtt_client.subscribe("maritime/threats/#", qos=1)
        else:
            logger.error(f"MQTT connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            threat_level = msg.topic.split("/")[-1].upper()
            
            # Dispatch to all configured channels
            if self.slack_webhook:
                self._send_slack_alert(payload, threat_level)
            
            if self.email_from and self.email_to:
                self._send_email_alert(payload, threat_level)
            
        except Exception as e:
            logger.error(f"Error handling alert message: {e}")

    def _send_slack_alert(self, alert_data, threat_level):
        """Send alert to Slack"""
        try:
            # Decode thumbnail
            thumbnail_b64 = alert_data.get("thumbnail", "")
            thumbnail_data = None
            if thumbnail_b64:
                thumbnail_data = base64.b64decode(thumbnail_b64)
            
            # Build Slack message
            color = {
                "RED": "#FF0000",
                "YELLOW": "#FFFF00",
                "ORANGE": "#FFA500",
                "GREEN": "#00FF00"
            }.get(threat_level, "#808080")
            
            message = {
                "attachments": [
                    {
                        "fallback": f"Maritime Threat Alert - {threat_level}",
                        "color": color,
                        "title": f"🚨 Maritime Threat Alert - {threat_level}",
                        "text": alert_data.get("sitrep", "No details available"),
                        "fields": [
                            {
                                "title": "Threat Count",
                                "value": str(alert_data.get("threat_count", 0)),
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": alert_data.get("timestamp", "Unknown"),
                                "short": True
                            },
                            {
                                "title": "Recommended Actions",
                                "value": "\n".join(alert_data.get("recommended_actions", [])),
                                "short": False
                            }
                        ],
                        "footer": "Maritime Surveillance System",
                        "ts": int(datetime.now().timestamp())
                    }
                ]
            }
            
            response = requests.post(
                self.slack_webhook,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Slack alert sent: {threat_level}")
            else:
                logger.error(f"Slack alert failed: {response.status_code}")
            
        except Exception as e:
            logger.error(f"Error sending Slack alert: {e}")

    def _send_email_alert(self, alert_data, threat_level):
        """Send alert via email with attachment"""
        try:
            subject = f"Maritime Threat Alert [{threat_level}]"
            
            # Build email body
            body = f"""
            Maritime Surveillance System Alert
            ====================================
            
            Threat Level: {threat_level}
            Timestamp: {alert_data.get('timestamp', 'Unknown')}
            Threat Count: {alert_data.get('threat_count', 0)}
            
            SITUATION REPORT:
            {alert_data.get('sitrep', 'No details available')}
            
            THREATS DETECTED:
            """
            
            for i, threat in enumerate(alert_data.get("threats", []), 1):
                body += f"\n{i}. {threat.get('threat_type', 'UNKNOWN')}"
                body += f"\n   Confidence: {threat.get('confidence', 0):.1%}"
                body += f"\n   Description: {threat.get('description', 'N/A')}"
                if "correlated_vessel" in threat:
                    body += f"\n   CORRELATED VESSEL: {threat['correlated_vessel'].get('name', 'Unknown')}"
            
            body += f"\n\nRECOMMENDED ACTIONS:\n"
            for action in alert_data.get("recommended_actions", []):
                body += f"- {action}\n"
            
            body += "\n\nEnd of Report"
            
            # Create email
            msg = MIMEMultipart()
            msg["From"] = self.email_from
            msg["To"] = ", ".join(self.email_to)
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))
            
            # Attach thumbnail if available
            thumbnail_b64 = alert_data.get("thumbnail", "")
            if thumbnail_b64:
                try:
                    thumbnail_data = base64.b64decode(thumbnail_b64)
                    image_part = MIMEImage(thumbnail_data, "jpeg")
                    image_part.add_header("Content-ID", "<threat_image>")
                    image_part.add_header("Content-Disposition", "attachment", filename="threat.jpg")
                    msg.attach(image_part)
                except Exception as e:
                    logger.warning(f"Could not attach thumbnail: {e}")
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email alert sent to {self.email_to}")
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")

    def run(self):
        """Start alert dispatcher"""
        logger.info("Starting Alert Dispatcher...")
        
        if not self.slack_webhook and not (self.email_from and self.email_to[0]):
            logger.warning("No Slack webhook or email configured. Alerts will not be dispatched.")
        
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
        
        try:
            self.mqtt_client.loop_forever()
        except KeyboardInterrupt:
            logger.info("Shutting down Alert Dispatcher")
            self.mqtt_client.disconnect()


if __name__ == "__main__":
    dispatcher = AlertDispatcher()
    dispatcher.run()
