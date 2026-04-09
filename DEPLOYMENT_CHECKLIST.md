# Deployment Checklist & First Run

## Pre-Deployment (< 30 minutes)

- [ ] Clone/download maritime_surveillance_agent directory
- [ ] Verify Docker & Docker Compose installed: `docker --version && docker compose --version`
- [ ] Copy `.env.example` to `.env`: `cp .env.example .env`
- [ ] Edit `.env` with your settings:
  - [ ] Set `RTSP_STREAMS` (or leave empty to use uploaded video only)
  - [ ] Set `SLACK_WEBHOOK_URL` (optional, or leave empty)
  - [ ] Set email credentials (optional, or leave empty)

## Validation Before Starting

```bash
# Check Docker is running
docker ps

# Validate docker-compose.yml
docker compose config

# Create required directories
mkdir -p maritime_surveillance_agent/{uploads,frames,videos,documents,detections}
```

## Startup

```bash
cd maritime_surveillance_agent

# Start all services (first time downloads images ~5-10 min)
docker compose up -d

# Monitor startup (wait 30-60 seconds for Ollama to pull model)
docker compose logs -f

# Verify all services running
docker compose ps
```

**Expected output**:
```
NAME                    STATUS
maritime_mqtt           Up
maritime_mistral        Up
maritime_video_ingestion Up
maritime_document_processor Up
maritime_cv_agent       Up
maritime_alert_dispatcher Up
maritime_websocket      Up
```

## First Test (5 minutes)

### Test 1: Access Dashboard

```bash
# Open browser: http://localhost:50000/dashboard.html
# You should see:
# - Status indicator (green = connected)
# - Stats panel (zeros initially)
# - Empty alert feeds
```

**If dashboard doesn't load**:
```bash
docker compose logs websocket_server | tail -20
# Check port 50000 is accessible
# Try: curl http://localhost:50000/dashboard.html
```

### Test 2: Upload Test Video

```bash
# Copy a sample maritime video
cp ~/Downloads/ship_video.mp4 maritime_surveillance_agent/uploads/test_video.mp4

# Monitor frame extraction
docker compose logs -f video_ingestion | grep "frame"

# Should see "Extracted X frames from test_video"
```

### Test 3: Monitor CV Agent

```bash
# In new terminal, watch threat detection
docker compose logs -f cv_agent | grep -E "(threat|THREAT|confidence)"

# If working, you'll see:
# - Frame analysis logs
# - JSON threat detections
# - MQTT publish confirmations
```

### Test 4: Check MQTT

```bash
# Connect to MQTT broker and subscribe to threats
docker exec -it maritime_mqtt mosquitto_sub -h localhost -t "maritime/threats/#"

# In another terminal, upload test video (from Test 2)
# You should see threat messages appear in real-time as JSON
```

### Test 5: Test Slack (if configured)

```bash
# Set SLACK_WEBHOOK_URL in .env, restart
docker compose down
docker compose up -d alert_dispatcher

# Upload test video
cp ~/Downloads/ship_video.mp4 maritime_surveillance_agent/uploads/test2.mp4

# Check Slack channel for alerts
# Should appear within 30 seconds
```

### Test 6: Test Email (if configured)

```bash
# Verify email settings in .env
docker compose logs alert_dispatcher | grep -E "(SMTP|email|sent)"

# Upload test video
cp ~/Downloads/ship_video.mp4 maritime_surveillance_agent/uploads/test3.mp4

# Check inbox for threat reports
```

## Troubleshooting Startup

### Issue: "Cannot connect to Docker daemon"
**Solution**: Start Docker Desktop or `sudo systemctl start docker`

### Issue: "Port 50000 already in use"
**Solution**: 
```bash
# Change port in docker-compose.yml
# Or kill existing process: sudo lsof -ti:50000 | xargs kill -9
```

### Issue: "Ollama model download timeout"
**Solution**: 
```bash
# Pull model manually first
docker exec maritime_mistral ollama pull llava
# Or use smaller model: ollama pull mistral:latest (text-only)
```

### Issue: "Video ingestion not extracting frames"
**Solution**:
```bash
# Check RTSP URL is valid
ffprobe rtsp://your_stream_url

# Or upload local video first
cp test_video.mp4 maritime_surveillance_agent/uploads/

# Check frame directory
ls -la maritime_surveillance_agent/frames/
```

### Issue: "CV agent not detecting threats"
**Solution**:
```bash
# Check model loaded
docker exec maritime_cv_agent ps aux | grep agent.py

# Check MQTT connectivity
docker compose logs cv_agent | grep "MQTT"

# Check threat confidence threshold not too high
docker compose logs cv_agent | grep "THREAT_CONFIDENCE"
```

## Production Readiness Checklist

- [ ] All 7 services running: `docker compose ps`
- [ ] Dashboard accessible: http://localhost:50000/dashboard.html
- [ ] Test alert generated and received (Slack/Email)
- [ ] Video frames being extracted: `ls maritime_surveillance_agent/frames | wc -l`
- [ ] No ERROR logs in 2 minutes: `docker compose logs --since 2m | grep ERROR`
- [ ] Database backups scheduled (if using Postgres for audit logs)
- [ ] Monitoring configured (Prometheus/Grafana optional)

## Next Steps

### 1. Configure Live RTSP Streams

Edit `.env`:
```bash
RTSP_STREAMS=rtsp://camera1.example.com:554/stream1,rtsp://camera2.example.com:554/stream2
```

Restart:
```bash
docker compose restart video_ingestion
docker compose logs -f video_ingestion
```

### 2. Upload MAYDAY Document

```bash
# Create sample MAYDAY
cat > maritime_surveillance_agent/uploads/mayday.txt << 'EOF'
MAYDAY MAYDAY MAYDAY
Vessel: MV Northern Star
MMSI: 123456789
Position: 40.7128° N, 74.0060° W
Status: SINKING
Engine room fire
Crew: 22 - Request immediate assistance
EOF

# Monitor processing
docker compose logs document_processor
```

### 3. Fine-tune Threat Detection

See `CUSTOMIZATION_GUIDE.md` for:
- Adding custom threat classes
- Adjusting confidence thresholds
- Regional threat variations

### 4. Set Up Persistence

Current setup keeps data in memory/containers. For production:

```bash
# Backup threat alerts
docker cp maritime_cv_agent:/app/detections ./detections_backup

# Archive frames
tar -czf frames_$(date +%Y%m%d).tar.gz maritime_surveillance_agent/frames/
```

### 5. Monitor Performance

```bash
# Check resource usage
docker stats

# CPU/Memory should stabilize after 1-2 minutes
# ~15-20% CPU per CV agent
# ~800MB-1.2GB RAM per CV agent
```

## Stopping & Restarting

```bash
# Stop all services (data preserved)
docker compose down

# Restart
docker compose up -d

# Full cleanup (caution: deletes data!)
docker compose down -v
```

## Scaling (Advanced)

### Horizontal Scaling (Multiple CV Agents)

```yaml
# In docker-compose.yml, duplicate cv_agent:

services:
  cv_agent_1:
    build: ./services/cv_agent
    depends_on:
      - mosquitto
      - mistral_ollama
  
  cv_agent_2:
    build: ./services/cv_agent
    depends_on:
      - mosquitto
      - mistral_ollama
```

Then:
```bash
docker compose up -d
```

Load-balancing via MQTT subscriptions (automatic).

### GPU Acceleration

Add to services requiring it:
```yaml
services:
  mistral_ollama:
    build: ./services/mistral_ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
  
  cv_agent:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

Requires `nvidia-docker` installed.

## Maintenance

### Weekly

```bash
# Cleanup old frames
find maritime_surveillance_agent/frames -mtime +7 -delete

# Check logs for errors
docker compose logs --since 7d | grep ERROR
```

### Monthly

```bash
# Prune unused Docker data
docker system prune -a

# Archive detections
tar -czf detections_$(date +%Y%m%d).tar.gz maritime_surveillance_agent/detections/

# Backup environment
cp .env .env.backup.$(date +%Y%m%d)
```

## Support Resources

- **Logs**: `docker compose logs <service_name>`
- **MQTT Debug**: `docker exec maritime_mqtt mosquitto_sub -h localhost -t "#"`
- **Threat Info**: See `THREAT_MODELS.md`
- **Customization**: See `CUSTOMIZATION_GUIDE.md`
- **API Docs**: MQTT topics in `QUICKSTART.md`

## Emergency Procedures

### System Overload (High CPU/Memory)

```bash
# Reduce frame extraction rate
# Edit docker-compose.yml:
# VIDEO_FRAME_INTERVAL=5  # Extract frame every 5 seconds (instead of 2)

docker compose up -d video_ingestion
```

### Missing Alerts

```bash
# Verify MQTT connectivity
docker compose logs mosquitto | grep -E "(error|failed)"

# Verify alert dispatcher running
docker compose ps alert_dispatcher

# Check configuration
docker compose config | grep -E "(EMAIL|SLACK)"
```

### Vessel Correlation Not Working

```bash
# Verify document processor
docker compose logs document_processor | head -20

# Check vessel registry
docker exec maritime_cv_agent ls -la /app/documents/

# Verify correlation enabled
docker compose logs cv_agent | grep "CORRELATION"
```

---

**Ready to go!** 🚀

Start with Step 1 above, then reference QUICKSTART.md for ongoing usage.

Questions? Check the docs or review logs: `docker compose logs -f`
