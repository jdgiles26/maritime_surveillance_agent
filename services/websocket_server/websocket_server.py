import os
import json
import asyncio
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WebSocketServer")

class WebSocketServer:
    def __init__(self):
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.ws_port = int(os.getenv("WS_PORT", 50000))
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        
        self.connected_clients = set()
        self.recent_alerts = []
        self.max_history = 100

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected")
            self.mqtt_client.subscribe("maritime/threats/#", qos=1)
        else:
            logger.error(f"MQTT connection failed: {rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            threat_level = msg.topic.split("/")[-1].upper()
            
            # Store in history
            alert = {
                "threat_level": threat_level,
                "timestamp": datetime.now().isoformat(),
                "data": payload
            }
            self.recent_alerts.append(alert)
            if len(self.recent_alerts) > self.max_history:
                self.recent_alerts.pop(0)
            
            # Broadcast to WebSocket clients
            asyncio.create_task(self._broadcast_alert(alert))
            
        except Exception as e:
            logger.error(f"Error handling MQTT message: {e}")

    async def _broadcast_alert(self, alert):
        """Broadcast alert to all connected WebSocket clients"""
        if not self.connected_clients:
            return
        
        message = json.dumps({
            "type": "threat_alert",
            "alert": alert
        })
        
        # Remove disconnected clients
        disconnected = set()
        for client in self.connected_clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
        
        self.connected_clients -= disconnected

    async def handle_client(self, websocket, path):
        """Handle WebSocket client connection"""
        self.connected_clients.add(websocket)
        logger.info(f"Client connected: {websocket.remote_address}")
        
        # Send recent alerts to new client
        for alert in self.recent_alerts:
            try:
                await websocket.send(json.dumps({
                    "type": "historical_alert",
                    "alert": alert
                }))
            except websockets.exceptions.ConnectionClosed:
                break
        
        try:
            async for message in websocket:
                # Handle client commands
                try:
                    cmd = json.loads(message)
                    if cmd.get("type") == "get_history":
                        await websocket.send(json.dumps({
                            "type": "alert_history",
                            "alerts": self.recent_alerts[-50:]  # Last 50
                        }))
                    elif cmd.get("type") == "get_stats":
                        stats = {
                            "total_alerts": len(self.recent_alerts),
                            "red_count": len([a for a in self.recent_alerts if a["threat_level"] == "RED"]),
                            "yellow_count": len([a for a in self.recent_alerts if a["threat_level"] == "YELLOW"]),
                            "orange_count": len([a for a in self.recent_alerts if a["threat_level"] == "ORANGE"]),
                            "connected_clients": len(self.connected_clients)
                        }
                        await websocket.send(json.dumps({
                            "type": "stats",
                            "stats": stats
                        }))
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from client: {message}")
                except Exception as e:
                    logger.error(f"Error processing client message: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"Client disconnected: {websocket.remote_address}")

    async def run_websocket_server(self):
        """Start WebSocket server"""
        logger.info(f"Starting WebSocket server on port {self.ws_port}")
        async with websockets.serve(self.handle_client, "0.0.0.0", self.ws_port):
            logger.info(f"WebSocket server listening on ws://0.0.0.0:{self.ws_port}")
            await asyncio.Future()  # run forever

    def run(self):
        """Start server"""
        logger.info("Starting WebSocket Alert Server...")
        
        # Connect to MQTT
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_start()
        
        # Start WebSocket server
        try:
            asyncio.run(self.run_websocket_server())
        except KeyboardInterrupt:
            logger.info("Shutting down WebSocket server")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


if __name__ == "__main__":
    server = WebSocketServer()
    server.run()
