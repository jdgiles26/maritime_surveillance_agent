# Maritime Surveillance System - Quick Start

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIDEO INGESTION                              │
│   ├─ RTSP/Live Streams (camera feeds)                           │
│   ├─ Uploaded Video Files (MP4, AVI, MOV, MKV)                  │
│   └─ YOLO Object Detection (parallel processing)                │
└─────────────────┬──────────────────────────────────────────────┘
                  │ MQTT (frames/new)
┌─────────────────▼──────────────────────────────────────────────┐
│         DOCUMENT PROCESSOR                                       │
│   ├─ PDF Extraction (MAYDAY, vessel info)                       │
│   └─ Mistral NLP (extract coordinates, vessel description)      │
└─────────────────┬──────────────────────────────────────────────┘
                  │ MQTT (documents/processed)
┌─────────────────▼──────────────────────────────────────────────┐
│         MARITIME CV AGENT (PRIMARY INTELLIGENCE)                │
│   ├─ Mistral Vision (llava/bakllava model)                      │
│   ├─ Threat Detection (smuggling, wrecks, weapons, etc.)        │
│   ├─ Correlation Engine (matches vessels to threats)            │
│   └─ SITREP Generation (threat level, actions, report)          │
└─────────────────┬──────────────────────────────────────────────┘
                  │ MQTT (threats/RED, YELLOW, ORANGE, GREEN)
        ┌─────────┴─────────┐
        │                   │
┌───────▼────────┐  ┌──────▼──────────┐
│ ALERT DISPATCHER│  │ WEBSOCKET SERVER │
├─ Slack         │  ├─ Real-time      │
├─ Email         │  ├─ Dashboard      │
└─────────────────┘  └──────────────────┘
```

## Prerequisites

- Docker & Docker Compose
- RTSP stream URLs (or pre-recorded video files)
- Slack webhook (optional)
- SMTP credentials (optional)

## Setup

### 1. Clone and configure

```bash
cd maritime_surveillance_agent
cp .env.example .env
```

### 2. Edit `.env` with your settings

```bash
# RTSP streams (comma-separated)
RTSP_STREAMS=rtsp://192.168.1.100:554/stream1,rtsp://example.com:554/stream2

# Slack alerts
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Email alerts
EMAIL_FROM=alerts@yourdomain.com
EMAIL_TO=commander@yourdomain.com
SMTP_USER=alerts@yourdomain.com
SMTP_PASSWORD=your_app_password
```

### 3. Start the system

```bash
docker compose up -d
```

This starts:
- **mosquitto** (MQTT broker) on port 1883 / 9001
- **mistral_ollama** (Mistral AI + vision) on port 11434
- **video_ingestion** (frame extraction from streams/uploads)
- **document_processor** (PDF vessel extraction)
- **cv_agent** (threat detection & correlation)
- **alert_dispatcher** (Slack/email)
- **websocket_server** (dashboard) on port 50000

### 4. Access the dashboard

Open in browser:
```
http://localhost:50000/dashboard.html
```

Wait 15-20 seconds for dashboard to connect. You'll see:
- Live threat counts (RED, YELLOW, ORANGE)
- Real-time threat feed
- Threat type breakdown
- System status

## Usage

### Upload a video for analysis

```bash
cp your_video.mp4 maritime_surveillance_agent/uploads/
```

The video is automatically split into frames and analyzed.

### Upload a MAYDAY document

```bash
# Create sample MAYDAY PDF
echo "MAYDAY MAYDAY MAYDAY
Vessel: MV Eastwind
MMSI: 123456789
Position: 40.7128° N, 74.0060° W
Status: SINKING
Crew: 15
Fire in engine room
Request immediate assistance" > maritime_surveillance_agent/uploads/mayday.txt
```

The system extracts vessel data and correlates it with live feeds.

### Check logs

```bash
docker compose logs -f cv_agent
docker compose logs -f alert_dispatcher
docker compose logs -f document_processor
```

## Threat Detection Classes

| Threat | Severity | Action |
|--------|----------|--------|
| **WEAPONS** | CRITICAL | Escalate to command, scramble response |
| **PIRATES** | CRITICAL | Intercept, request naval support |
| **WRECKS** | HIGH | Dispatch recovery team |
| **OIL SPILLS** | HIGH | Alert coastal authority |
| **FIRES** | HIGH | Dispatch emergency services |
| **SMUGGLING** | HIGH | Investigate, intercept |
| **DARK_VESSEL** | MEDIUM | Monitor closely |
| **VESSEL_GATHERING** | MEDIUM | Investigate coordination |
| **MILITARY_VESSEL** | MEDIUM | Track, report |
| **ENDANGERED_WATERS** | LOW | Alert authorities |

## Correlation Engine

If a MAYDAY PDF is uploaded with:
```
Vessel: MV Eastwind
MMSI: 123456789
Coordinates: 40.7° N, 74.0° W
```

The CV agent will:
1. Register the vessel data
2. Scan live video feeds within 5nm radius
3. Match visual characteristics (color, size, markings)
4. Publish **PRIORITY** alert if found
5. Include vessel details in SITREP

## MQTT Topics

### Published Topics

```
maritime/threats/RED       → Critical threats (weapons, pirates, wrecks)
maritime/threats/YELLOW    → High-confidence threats
maritime/threats/ORANGE    → Medium-confidence threats
maritime/threats/GREEN     → Low-risk observations
maritime/frames/new        → New frame extracted
maritime/documents/processed → Vessel data extracted from PDF
```

### Message Format

```json
{
  "timestamp": "2024-01-15T14:30:00.000Z",
  "threat_level": "RED",
  "threat_count": 3,
  "thumbnail": "base64_encoded_jpeg",
  "sitrep": "MARITIME THREAT REPORT...",
  "threats": [
    {
      "threat_type": "WEAPONS",
      "confidence": 0.95,
      "location": "port side",
      "description": "Mounted gun turret visible on deck",
      "correlated_vessel": {
        "name": "Unknown Vessel",
        "mmsi": "123456789",
        "alert_type": "MILITARY"
      }
    }
  ],
  "recommended_actions": [
    "ESCALATE to command",
    "Scramble response vessel"
  ]
}
```

## Configuration Tuning

### Threat Confidence Threshold

In `docker-compose.yml`:
```yaml
THREAT_CONFIDENCE_THRESHOLD=0.6  # 0.0-1.0 (lower = more alerts)
```

### Frame Extraction Rate

```yaml
VIDEO_FRAME_INTERVAL=2  # Extract frame every 2 seconds (1 = every frame)
```

### Correlation Search Radius

In `services/cv_agent/agent.py`:
```python
"radius": vessel_data.get("search_radius", 5),  # nautical miles
```

## Troubleshooting

### No frames extracted
```bash
docker compose logs video_ingestion
# Check RTSP_STREAMS in .env are valid
# Test RTSP: ffprobe rtsp://your_stream
```

### Ollama/Mistral not responding
```bash
docker compose logs mistral_ollama
# Pull model manually
docker exec maritime_mistral ollama pull llava
# Or use mistral:latest for text-only model
```

### Alerts not sending
```bash
docker compose logs alert_dispatcher
# Verify Slack webhook URL and email credentials
# Test SMTP manually with:
# python3 -c "import smtplib; s=smtplib.SMTP('smtp.gmail.com', 587); print('OK')"
```

### Dashboard not connecting
```bash
docker compose logs websocket_server
# Port 50000 must be accessible
# Check firewall rules
```

## Production Deployment

For multi-location deployments:

1. **Scale horizontally**: Deploy CV agents on separate nodes
2. **Use managed MQTT broker** (AWS IoT Core, Azure Event Hub, HiveMQ Cloud)
3. **Kubernetes manifests**: See `kubernetes/` directory
4. **High-availability**: Use Redis for Slack rate limiting, PostgreSQL for audit logs
5. **GPU acceleration**: Add `runtime: nvidia` to cv_agent service for faster inference

## Support

For questions or custom threat models, check the threat detection prompts in `services/cv_agent/agent.py` and modify `_build_threat_detection_prompt()`.

---
**System Status**: Monitoring maritime threat landscape
