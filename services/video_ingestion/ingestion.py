import os
import cv2
import numpy as np
from pathlib import Path
from datetime import datetime
import paho.mqtt.client as mqtt
import json
import logging
import threading
import subprocess
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("VideoIngestion")

class VideoIngestionService:
    def __init__(self):
        self.mqtt_broker = os.getenv("MQTT_BROKER", "localhost")
        self.mqtt_port = int(os.getenv("MQTT_PORT", 1883))
        self.frame_interval = int(os.getenv("VIDEO_FRAME_INTERVAL", 2))
        self.frame_dir = Path("/app/frames")
        self.upload_dir = Path("/app/uploads")
        self.video_dir = Path("/app/videos")
        
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        
        # Create directories
        self.frame_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.video_dir.mkdir(parents=True, exist_ok=True)
        
        # Stream sources (configurable)
        self.rtsp_streams = os.getenv("RTSP_STREAMS", "").split(",")
        self.rtsp_streams = [s.strip() for s in self.rtsp_streams if s.strip()]

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("MQTT connected")
        else:
            logger.error(f"MQTT connection failed: {rc}")

    def capture_from_rtsp(self, rtsp_url, stream_name):
        """Capture frames from RTSP stream"""
        logger.info(f"Starting RTSP capture: {stream_name}")
        frame_count = 0
        
        try:
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer
            
            if not cap.isOpened():
                logger.error(f"Failed to open RTSP stream: {rtsp_url}")
                return
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame from {stream_name}, reconnecting...")
                    cap.release()
                    import time
                    time.sleep(5)
                    cap = cv2.VideoCapture(rtsp_url)
                    continue
                
                frame_count += 1
                
                # Extract frame every N frames
                if frame_count % self.frame_interval == 0:
                    timestamp = datetime.now().isoformat()
                    frame_filename = f"{stream_name}_{timestamp.replace(':', '-')}.jpg"
                    frame_path = self.frame_dir / frame_filename
                    
                    # Save frame
                    cv2.imwrite(str(frame_path), frame)
                    
                    # Publish MQTT notification
                    self.mqtt_client.publish(
                        "maritime/frames/new",
                        json.dumps({
                            "frame_path": str(frame_path),
                            "stream": stream_name,
                            "timestamp": timestamp
                        }),
                        qos=1
                    )
                    
                    logger.info(f"Captured frame: {frame_filename}")
                
        except Exception as e:
            logger.error(f"Error capturing from {stream_name}: {e}")
        finally:
            cap.release()

    def process_uploaded_video(self, video_path):
        """Extract frames from uploaded video file"""
        logger.info(f"Processing uploaded video: {video_path}")
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_interval = int(fps * self.frame_interval)  # Extract every N seconds
            frame_count = 0
            extracted_count = 0
            
            video_name = Path(video_path).stem
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % frame_interval == 0:
                    timestamp = datetime.now().isoformat()
                    frame_filename = f"{video_name}_frame_{extracted_count:05d}_{timestamp.replace(':', '-')}.jpg"
                    frame_path = self.frame_dir / frame_filename
                    
                    cv2.imwrite(str(frame_path), frame)
                    
                    self.mqtt_client.publish(
                        "maritime/frames/new",
                        json.dumps({
                            "frame_path": str(frame_path),
                            "source": "uploaded_video",
                            "video": video_name,
                            "timestamp": timestamp
                        }),
                        qos=1
                    )
                    
                    extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {extracted_count} frames from {video_name}")
            
        except Exception as e:
            logger.error(f"Error processing video: {e}")

    def monitor_upload_directory(self):
        """Monitor for new uploaded video files"""
        processed_videos = set()
        
        while True:
            try:
                video_files = list(self.upload_dir.glob("*.mp4")) + \
                             list(self.upload_dir.glob("*.avi")) + \
                             list(self.upload_dir.glob("*.mov")) + \
                             list(self.upload_dir.glob("*.mkv"))
                
                for video_path in video_files:
                    if str(video_path) not in processed_videos:
                        self.process_uploaded_video(video_path)
                        processed_videos.add(str(video_path))
                
                import time
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error monitoring upload directory: {e}")
                import time
                time.sleep(5)

    def run(self):
        """Start video ingestion service"""
        logger.info("Starting Video Ingestion Service...")
        
        self.mqtt_client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
        self.mqtt_client.loop_start()
        
        threads = []
        
        # Start RTSP capture threads
        for rtsp_url in self.rtsp_streams:
            stream_name = rtsp_url.split("/")[-1] or "stream"
            thread = threading.Thread(
                target=self.capture_from_rtsp,
                args=(rtsp_url, stream_name),
                daemon=True
            )
            thread.start()
            threads.append(thread)
        
        # Start upload monitoring thread
        upload_thread = threading.Thread(
            target=self.monitor_upload_directory,
            daemon=True
        )
        upload_thread.start()
        threads.append(upload_thread)
        
        logger.info(f"Started {len(threads)} ingestion thread(s)")
        
        try:
            for thread in threads:
                thread.join()
        except KeyboardInterrupt:
            logger.info("Shutting down Video Ingestion Service")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()


if __name__ == "__main__":
    service = VideoIngestionService()
    service.run()
