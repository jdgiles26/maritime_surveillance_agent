# Maritime Surveillance System - Documentation Index

## 📚 Complete Documentation Structure

### Quick Navigation

| Document | Purpose | Read Time |
|----------|---------|-----------|
| **[README.md](README.md)** | System overview, features, quick start | 5 min |
| **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** | Step-by-step deployment & first run | 15 min |
| **[QUICKSTART.md](QUICKSTART.md)** | Setup, configuration, troubleshooting | 10 min |
| **[THREAT_MODELS.md](THREAT_MODELS.md)** | Detailed threat class definitions | 20 min |
| **[REPORT_FORMAT.md](REPORT_FORMAT.md)** | Alert report structure & formats | 10 min |
| **[CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)** | How to customize & train the model | 20 min |

---

## 🚀 Get Started (Choose Your Path)

### Path 1: I Just Want It Running (30 min)

1. Read: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - "Pre-Deployment"
2. Run: `docker compose up -d`
3. Access: http://localhost:50000/dashboard.html
4. Done! System is monitoring.

### Path 2: I Want to Understand Everything (1 hour)

1. Read: [README.md](README.md) - overview & architecture
2. Read: [THREAT_MODELS.md](THREAT_MODELS.md) - what it detects
3. Read: [REPORT_FORMAT.md](REPORT_FORMAT.md) - alert structure
4. Read: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - deployment
5. Run: `docker compose up -d && docker compose logs -f`

### Path 3: I Want to Customize It (2 hours)

1. Complete "Path 2" above
2. Read: [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md)
3. Edit: `services/cv_agent/agent.py` threat detection prompt
4. Test: Upload video and monitor logs
5. Iterate: Fine-tune threat thresholds and actions

---

## 📋 File Reference

### Core Documentation

```
📁 maritime_surveillance_agent/
├── README.md                      ← Start here
├── DEPLOYMENT_CHECKLIST.md        ← Before first run
├── QUICKSTART.md                  ← Setup & usage
├── THREAT_MODELS.md               ← Threat definitions
├── REPORT_FORMAT.md               ← Alert formats
├── CUSTOMIZATION_GUIDE.md         ← Advanced tuning
└── SAMPLE_REPORT.txt              ← Example output
```

### Configuration Files

```
├── .env.example                   ← Copy to .env
├── docker-compose.yml             ← Service orchestration
├── mosquitto.conf                 ← MQTT broker config
```

### Source Code

```
├── 📁 services/
│   ├── 📁 video_ingestion/
│   │   ├── Dockerfile
│   │   ├── ingestion.py           ← RTSP & video processing
│   │   └── requirements.txt
│   ├── 📁 document_processor/
│   │   ├── Dockerfile
│   │   ├── processor.py           ← PDF vessel extraction
│   │   └── requirements.txt
│   ├── 📁 cv_agent/
│   │   ├── Dockerfile
│   │   ├── agent.py               ← THREAT DETECTION ENGINE
│   │   └── requirements.txt
│   ├── 📁 alert_dispatcher/
│   │   ├── Dockerfile
│   │   ├── dispatcher.py          ← Slack/Email alerts
│   │   └── requirements.txt
│   └── 📁 websocket_server/
│       ├── Dockerfile
│       ├── websocket_server.py    ← Live dashboard
│       └── requirements.txt
└── dashboard.html                 ← Web interface
```

---

## 🎯 Quick Reference by Role

### For Operations Teams (Using the System)

Read in order:
1. [README.md](README.md) - "What It Detects"
2. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - "Startup"
3. [QUICKSTART.md](QUICKSTART.md) - "Usage" section
4. [THREAT_MODELS.md](THREAT_MODELS.md) - Threat definitions for your region

### For System Administrators (Deploying/Maintaining)

Read in order:
1. [README.md](README.md) - Full section
2. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - All sections
3. [QUICKSTART.md](QUICKSTART.md) - "Configuration" & "Troubleshooting"
4. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - "Maintenance" section

### For AI/ML Engineers (Customizing Detection)

Read in order:
1. [THREAT_MODELS.md](THREAT_MODELS.md) - Full section
2. [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - All sections
3. `services/cv_agent/agent.py` - Code review
4. [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - "Testing Your Changes"

### For Security Teams (Understanding Data)

Read in order:
1. [REPORT_FORMAT.md](REPORT_FORMAT.md) - Alert structure
2. [THREAT_MODELS.md](THREAT_MODELS.md) - Each threat class
3. [QUICKSTART.md](QUICKSTART.md) - "MQTT Topics"

### For Developers (Contributing)

Read in order:
1. [README.md](README.md) - Architecture section
2. Review all services in `services/*/`
3. [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - Code examples
4. Check individual Dockerfiles

---

## 🔍 Find Information By Topic

### "How do I..."

| Question | Answer | Doc |
|----------|--------|-----|
| Get it running? | Follow deployment steps | DEPLOYMENT_CHECKLIST.md |
| Access the dashboard? | Open http://localhost:50000/dashboard.html | QUICKSTART.md |
| Understand threat levels? | See threat class definitions | THREAT_MODELS.md |
| Add a new threat type? | See customization section | CUSTOMIZATION_GUIDE.md |
| Fix a problem? | Check troubleshooting | QUICKSTART.md |
| Set up Slack alerts? | Configure .env file | QUICKSTART.md |
| See sample output? | Read SAMPLE_REPORT.txt | SAMPLE_REPORT.txt |
| Change alert format? | Edit report generation code | CUSTOMIZATION_GUIDE.md |

### "What does [term] mean?"

| Term | Explanation | Doc |
|------|-------------|-----|
| MQTT | Message broker for service communication | README.md, QUICKSTART.md |
| Mistral | AI language model for threat detection | README.md, THREAT_MODELS.md |
| Correlation | Matching vessel data to video threats | CUSTOMIZATION_GUIDE.md |
| CPA | Closest Point of Approach (collision risk) | THREAT_MODELS.md |
| Confidence | Probability score of threat (0.0-1.0) | THREAT_MODELS.md |
| SITREP | Situation Report (commander's brief) | REPORT_FORMAT.md |
| AIS | Automatic Identification System (vessel tracking) | THREAT_MODELS.md |
| RTSP | Real-Time Streaming Protocol (video source) | QUICKSTART.md |

---

## 📖 Reading Recommendations

### To Understand the Threat Model (15 min)

1. [THREAT_MODELS.md](THREAT_MODELS.md) - Sections 1-2 (Overview & 12 Threat Classes)
2. Skip to your area of interest (e.g., section "1. DARK_VESSEL")

### To Troubleshoot Alerts Not Arriving (10 min)

1. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - "Troubleshooting Startup"
2. [QUICKSTART.md](QUICKSTART.md) - "Troubleshooting"
3. Run: `docker compose logs alert_dispatcher`

### To Improve Detection Accuracy (30 min)

1. [THREAT_MODELS.md](THREAT_MODELS.md) - "Performance Tuning"
2. [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - "Fine-tune Threat Detection Prompt"
3. Edit and test prompt modifications

### To Scale to Multiple Cameras (20 min)

1. [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - "9. Seasonal & Weather Adjustments"
2. [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - "Scaling (Advanced)"
3. Update docker-compose.yml with multiple services

---

## 🆘 Troubleshooting Map

| Problem | First Check | Docs | Command |
|---------|-----------|------|---------|
| Services not starting | Docker running? | DEPLOYMENT_CHECKLIST.md | `docker compose ps` |
| Dashboard blank | WebSocket connected? | QUICKSTART.md | `curl http://localhost:50000` |
| No threats detected | Video uploaded? | DEPLOYMENT_CHECKLIST.md | `ls maritime_surveillance_agent/uploads/` |
| Mistral not responding | Model downloaded? | QUICKSTART.md | `docker exec maritime_mistral ollama list` |
| Alerts not sending | Configuration correct? | QUICKSTART.md | `docker compose logs alert_dispatcher` |
| MQTT not publishing | Broker running? | QUICKSTART.md | `docker compose ps mosquitto` |
| High CPU/Memory | Frame rate too high? | CUSTOMIZATION_GUIDE.md | Edit `VIDEO_FRAME_INTERVAL` |

---

## 📊 Feature Comparison

| Feature | Available | Doc |
|---------|-----------|-----|
| Real-time threat detection | ✅ | THREAT_MODELS.md |
| Multi-source ingestion (RTSP/video/PDF) | ✅ | README.md |
| 12 threat classes | ✅ | THREAT_MODELS.md |
| Confidence scoring | ✅ | THREAT_MODELS.md |
| Vessel correlation (MAYDAY matching) | ✅ | CUSTOMIZATION_GUIDE.md |
| Slack notifications | ✅ | QUICKSTART.md |
| Email with photos | ✅ | QUICKSTART.md |
| WebSocket dashboard | ✅ | QUICKSTART.md |
| MQTT message publishing | ✅ | QUICKSTART.md |
| Customizable threat prompts | ✅ | CUSTOMIZATION_GUIDE.md |
| Multi-frame confirmation | ✅ | CUSTOMIZATION_GUIDE.md |
| Historical tracking | 🔄 In-memory (add Postgres for persistence) | CUSTOMIZATION_GUIDE.md |
| GPU acceleration | ✅ (optional) | DEPLOYMENT_CHECKLIST.md |
| Kubernetes manifests | 🏗️ Coming soon | — |

---

## 📞 Support

### For Documentation Issues

Check if your question is answered in:
1. [README.md](README.md) - Quick overview
2. [QUICKSTART.md](QUICKSTART.md) - Practical guide
3. [THREAT_MODELS.md](THREAT_MODELS.md) - Threat definitions
4. [CUSTOMIZATION_GUIDE.md](CUSTOMIZATION_GUIDE.md) - Advanced topics

### For Deployment Issues

Follow [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - "Troubleshooting Startup" section

### For Code Questions

Review the service in `services/[service_name]/` and check inline documentation

---

## 📦 Version & Updates

| Component | Version | Status |
|-----------|---------|--------|
| System | 1.0 | ✅ Production Ready |
| Documentation | 2.0 | ✅ Complete |
| Threat Model | 1.2 (12 classes) | ✅ Stable |
| Mistral AI | Latest | ✅ Auto-updating |
| Docker Compose | v3.9 | ✅ Compatible |

---

## 🎓 Learning Path

**Beginner** (1-2 hours)
→ README.md → DEPLOYMENT_CHECKLIST.md → QUICKSTART.md

**Intermediate** (2-4 hours)
→ THREAT_MODELS.md → REPORT_FORMAT.md → Source code review

**Advanced** (4-8 hours)
→ CUSTOMIZATION_GUIDE.md → Code modifications → Testing & iteration

---

## Last Updated

- Documentation: 2024-01-15
- System: Production Ready
- Threat Classes: 12
- Services: 7

---

**Ready to get started?** → Go to [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

**Questions?** → Check the docs above or review logs: `docker compose logs -f`
