# Alert Report Format - Professional Maritime Standards

## Report Structure

All alerts (Email, Slack, Dashboard, MQTT) follow this professional format:

```
======================================================================
MARITIME SURVEILLANCE ALERT REPORT
======================================================================
Report Time: YYYY-MM-DD HH:MM:SS UTC
Overall Threat Level: RED/YELLOW/ORANGE/GREEN

SUMMARY
======================================================================
Total Threats Detected: [N]
High-Confidence Threats (>75%): [N]
Average AI Confidence Score: [X.X]%

SUSPICIOUS ACTIVITIES
======================================================================
[Activity 1 description, Activity 2 description, Activity 3 description]

THREAT BREAKDOWN
======================================================================
• THREAT_TYPE_1: [N] detection(s) - Confidence: XX.X%
• THREAT_TYPE_2: [N] detection(s) - Confidence: XX.X%
• THREAT_TYPE_3: [N] detection(s) - Confidence: XX.X%

RECOMMENDED ACTIONS
======================================================================
🔴 [Action 1 - for CRITICAL/RED threats]
🟡 [Action 2 - for HIGH/YELLOW threats]
🟢 [Action 3 - for MEDIUM/ORANGE threats]

THREAT DETAILS (Optional - Email only)
======================================================================
1. THREAT_TYPE_1
   Location in Frame: [port side, bow, center, etc.]
   Confidence: XX.X%
   Description: [Detailed observation of what AI detected]
   
   (If correlated with vessel)
   ⚠️  CORRELATED WITH VESSEL
   Name: [Vessel Name]
   MMSI: [Maritime Mobile Service Identity]
   Alert Type: [MAYDAY, MILITARY, etc.]
   Coordinates: [Latitude, Longitude]

======================================================================
[Threat photo attached as JPEG]

This is an automated alert from the Maritime Surveillance System.
Timestamp: YYYY-MM-DD HH:MM:SS UTC
Threat Level: [LEVEL]
======================================================================
```

## Threat Level Mapping

| Level | Color | Triggers | Response Time |
|-------|-------|----------|----------------|
| **RED** | 🔴 | Weapons, Pirates, Fire, Wreck, Correlated Vessel, Confidence ≥90% | Immediate (< 1 min) |
| **YELLOW** | 🟡 | High threats (75-89% confidence), Military vessel, Collision risk | Urgent (< 5 min) |
| **ORANGE** | 🟠 | Medium threats (60-74% confidence) | Routine (< 30 min) |
| **GREEN** | 🟢 | Low threats (< 60%), monitoring only | Information only |

## Recommended Actions Legend

### 🔴 CRITICAL Actions (RED Level)

```
🔴 ESCALATE TO COMMAND - Armed threat confirmed
🔴 Scramble response vessel immediately
🔴 Contact naval authorities for support
🔴 EMERGENCY - Dispatch rescue vessels
🔴 Alert coast guard and emergency services
🔴 URGENT: Life safety situation - All hands to rescue stations
🔴 PRIORITY: Match confirmed - Correlated with vessel report
🔴 Intercept and render assistance immediately
```

### 🟡 HIGH Actions (YELLOW Level)

```
🟡 Challenge vessel on VHF
🟡 Request AIS status and intentions
🟡 Maintain surveillance
🟡 Flag vessel for inspection
🟡 Request vessel boarding authorization
🟡 Monitor for coordinated activity
🟡 Log all vessel identities and positions
🟡 Check for known smuggling routes
🟡 Alert environmental protection agency
🟡 Dispatch pollution response team
🟡 Issue collision warning to both vessels
🟡 Monitor CPA and vessel speeds
🟡 Prepare emergency coordination if needed
```

### 🟢 MEDIUM Actions (ORANGE/GREEN Level)

```
🟢 Monitor for potential violations
🟢 Log proximity to restricted zone
🟢 Monitor vessel movements closely
🟢 Log vessel details and trajectory
🟢 Maintain safe distance
🟢 Attempt to identify vessel
🟢 Request AIS activation
🟢 Cross-reference visual characteristics
```

## Slack Message Format

```
╔════════════════════════════════════════════════════════════════════╗
║  🚨 MARITIME SURVEILLANCE ALERT - [THREAT_LEVEL]                   ║
╠════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Report Time: 2026-03-09 14:45:33 UTC                               ║
║  Threats Detected: 5                                                ║
║                                                                      ║
║  Threat Types:                                                       ║
║  • DARK_VESSEL (87.4%)                                               ║
║    Unlit vessel running without navigation lights...                ║
║                                                                      ║
║  • COLLISION_RISK (75.6%)                                            ║
║    Two vessels on converging course with CPA 0.3nm...               ║
║                                                                      ║
║  • OIL_SPILL (79.8%)                                                 ║
║    Surface discoloration pattern consistent with...                 ║
║                                                                      ║
║  Recommended Actions:                                               ║
║  🟡 Challenge vessel on VHF                                          ║
║  🟡 Request AIS status and intentions                                ║
║  🟡 Alert environmental protection agency                            ║
║                                                                      ║
║  Footer: Maritime Surveillance System | Automated Alert             ║
╚════════════════════════════════════════════════════════════════════╝
```

## Email Message Format

```
Subject: [THREAT_LEVEL] Maritime Threat Alert - YYYY-MM-DD HH:MM UTC

======================================================================
MARITIME SURVEILLANCE ALERT REPORT
======================================================================
Report Time: YYYY-MM-DD HH:MM:SS UTC
Overall Threat Level: [THREAT_LEVEL]

SUMMARY
======================================================================
Total Threats Detected: 5
High-Confidence Threats (>75%): 4
Average AI Confidence Score: 83.2%

SUSPICIOUS ACTIVITIES
======================================================================
Unlit vessel running without navigation lights, Two vessels on 
converging course with CPA of 0.3 nautical miles, Multiple small 
boats clustered together in coordinated formation, Surface 
discoloration pattern consistent with oil spill

THREAT BREAKDOWN
======================================================================
• DARK_VESSEL: 1 detection(s) - Confidence: 87.4%
• COLLISION_RISK: 1 detection(s) - Confidence: 75.6%
• VESSEL_GATHERING: 2 detection(s) - Confidence: 81.2%
• OIL_SPILL: 1 detection(s) - Confidence: 79.8%

RECOMMENDED ACTIONS
======================================================================
🟡 Challenge vessel on VHF
🟡 Request AIS status and intentions
🟡 Monitor for coordinated activity
🟡 Log all vessel identities and positions
🟡 Alert environmental protection agency
🟡 Dispatch pollution response team
🟡 Issue collision warning to both vessels
🟡 Monitor CPA and vessel speeds

THREAT DETAILS
======================================================================

1. DARK_VESSEL
   Location in Frame: port side, 35% horizontal, 45% vertical
   Confidence: 87.4%
   Description: Unlit vessel running without navigation lights at 
   night, approximately 500m distance, high speed maneuvering

2. COLLISION_RISK
   Location in Frame: bow, 60% horizontal, 50% vertical
   Confidence: 75.6%
   Description: Two vessels on converging course with CPA of 0.3 
   nautical miles, closing speed ~12 knots

3. VESSEL_GATHERING
   Location in Frame: center field
   Confidence: 81.2%
   Description: Multiple small boats clustered together in tight 
   formation, coordinated maneuvers observed

4. OIL_SPILL
   Location in Frame: port side of channel
   Confidence: 79.8%
   Description: Surface discoloration pattern consistent with oil 
   spill, approximately 2 hectares visible, rainbow sheen indicates 
   refined products

======================================================================
[THREAT IMAGE ATTACHED: threat_detection.jpg]

This is an automated alert from the Maritime Surveillance System.
Timestamp: 2026-03-09 14:45:33 UTC
Threat Level: HIGH

For operational security, do not forward to external recipients.
======================================================================
```

## Dashboard Display

### Threat Card (Live Feed)

```
┌─────────────────────────────────────────┐
│ 🔴 CRITICAL THREAT                      │
│ Report Time: 14:45:33                   │
│                                         │
│ Threat Count: 5                         │
│                                         │
│ Overview:                               │
│ Unlit vessel running without navigation │
│ lights at night, approximately 500m...  │
│                                         │
│ [2026-03-09 14:45:33 UTC]               │
└─────────────────────────────────────────┘
```

### Statistics Panel

```
┌──────────────┐  ┌──────────────┐
│ Total Alerts │  │🔴 Critical   │
│      87      │  │      12      │
└──────────────┘  └──────────────┘

┌──────────────┐  ┌──────────────┐
│🟡 Warning    │  │Connected     │
│      34      │  │   3 clients  │
└──────────────┘  └──────────────┘
```

## Customization

### Change Report Format

Edit `services/cv_agent/agent.py`:

```python
def _generate_commander_report(self, threats):
    # Modify format here
    # Return string with your custom structure
```

### Adjust Threat Level Thresholds

Edit `services/cv_agent/agent.py`:

```python
def _calculate_threat_level(self, threats):
    if max_severity >= 0.9:
        return "RED"      # Modify this threshold
    elif max_severity >= 0.75:
        return "YELLOW"   # And this one
```

### Change Action Messages

Edit `services/cv_agent/agent.py`:

```python
def _generate_actions(self, threats):
    # Customize action messages here
    # Use emoji prefixes: 🔴 🟡 🟢 for color coding
```

### Custom Email Template

Edit `services/alert_dispatcher/dispatcher.py`:

```python
def _send_email_alert(self, alert_data, threat_level):
    # Customize email body HTML/text format here
    body = f"""Your custom template..."""
```

---

**Report Version**: 2.0  
**Format Standard**: Maritime Surveillance System  
**Last Updated**: 2024-01-15  

For threat definitions, see `THREAT_MODELS.md`  
For customization, see `CUSTOMIZATION_GUIDE.md`
