# How to Customize & Train Your Threat Detection Model

## Quick Reference: Threat Model Components

Every threat in your system has these properties:

```python
{
    "threat_type": "DARK_VESSEL",              # Class name (must match prompt)
    "confidence": 0.87,                        # 0.0-1.0 score
    "location": "port side",                   # Frame quadrant
    "description": "Unlit vessel...",          # Detailed observation
    "severity": "HIGH",                        # CRITICAL/HIGH/MEDIUM/LOW
    "coordinates_frame": "35%, 45%"            # Position in frame
}
```

---

## Common Threat Model Customizations

### 1. Add Domain-Specific Threat (e.g., Illegal Fishing)

**File**: `services/cv_agent/agent.py`

**Step 1**: Add to detection prompt

```python
def _build_threat_detection_prompt(self):
    return """...
    13. ILLEGAL_FISHING: Bottom trawling in marine sanctuary, net dragging in protected zone, beam trawler in 3nm zone
    ...
    """
```

**Step 2**: Add actions

```python
elif "illegal_fishing" in threat_type:
    if conf >= 0.85:
        actions.add("🟡 Alert fisheries enforcement authority")
        actions.add("🟡 Request boarding inspection")
        actions.add("🟡 Document fishing gear and catch")
```

**Step 3**: Test

```bash
# Upload a photo of a trawler
docker compose logs cv_agent | grep "illegal_fishing"
```

---

### 2. Change Alert Sensitivity

**Current default**: 0.6 confidence (moderate)

**Options**:

```yaml
# In docker-compose.yml, change:
THREAT_CONFIDENCE_THRESHOLD=0.75  # Only very confident threats
THREAT_CONFIDENCE_THRESHOLD=0.5   # Catch more potential threats
```

**Effect**:

| Threshold | Result |
|-----------|--------|
| 0.4 | Very sensitive, ~40% false positives |
| 0.6 | **Recommended** - balanced |
| 0.75 | Conservative, may miss subtle threats |
| 0.85 | Critical only, high-confidence only |

---

### 3. Adjust Threat Severity Mapping

**File**: `services/cv_agent/agent.py`

**Current logic**:

```python
def _calculate_threat_level(self, threats):
    if not threats:
        return "GREEN"
    max_severity = max([t.get("confidence", 0) for t in threats], default=0)
    if max_severity >= 0.9:
        return "RED"      # Critical - escalate to command
    elif max_severity >= 0.75:
        return "YELLOW"   # Warning - heightened alert
    else:
        return "ORANGE"   # Caution - monitor closely
```

**Custom mapping** (e.g., all weapons = RED regardless of confidence):

```python
def _calculate_threat_level(self, threats):
    # CRITICAL threats always RED
    critical = ["WEAPONS", "PIRATE", "FIRE", "WRECK"]
    if any(t.get("threat_type") in critical for t in threats):
        return "RED"
    
    # Correlated vessel always at least YELLOW
    if any("correlated_vessel" in t for t in threats):
        return "YELLOW"
    
    max_severity = max([t.get("confidence", 0) for t in threats], default=0)
    if max_severity >= 0.9:
        return "RED"
    elif max_severity >= 0.75:
        return "YELLOW"
    else:
        return "ORANGE"
```

---

### 4. Modify Alert Actions by Region

**File**: `services/cv_agent/agent.py`

**Add geographic context**:

```python
def _generate_actions(self, threats, region="INTERNATIONAL"):
    actions = set()
    
    # Region-specific responses
    region_actions = {
        "PIRACY": {
            "GULF_OF_ADEN": [
                "🔴 Contact UKMTO (UK Maritime Trade Operations)",
                "🔴 Request naval escort from international coalition"
            ],
            "GULF_OF_MEXICO": [
                "🔴 Contact USCG Sector"
            ],
            "SOUTH_CHINA_SEA": [
                "🔴 Notify littoral state authorities"
            ]
        }
    }
    
    for threat in threats:
        ttype = threat.get("threat_type", "")
        if ttype in region_actions:
            if region in region_actions[ttype]:
                actions.update(region_actions[ttype][region])
    
    return list(actions)
```

---

### 5. Fine-Tune Threat Detection Prompt

**File**: `services/cv_agent/agent.py`, method `_build_threat_detection_prompt()`

**Examples of custom prompts**:

**For Harbor/Port Operations**:

```python
return """Analyze this harbor scene for threats.

MARITIME THREAT CLASSES:
1. COLLISION_RISK: Vessels maneuvering in close quarters
2. GROUNDING_RISK: Vessels in shallow water near pier/rocks
3. POLLUTION: Fluid discharge from vessel
4. UNAUTHORIZED_ENTRY: Vessel approaching restricted berth
5. CARGO_THEFT: Suspicious activity around cargo operations
...
"""
```

**For Open Ocean**:

```python
return """Analyze this open ocean maritime scene.

FOCUS ON:
1. DISTANT_VESSEL: Any unidentified vessel >5nm away
2. WEATHER_HAZARD: Storm cell, poor visibility
3. ABANDONMENT: Life raft, debris field, survival equipment
...
"""
```

**For Coastal Anti-Trafficking**:

```python
return """Scan for smuggling indicators.

LOOK FOR:
1. SPEEDBOAT: <50ft, open hull, high horsepower indicators
2. DARK_RUNNING: No navigation lights, operating at night
3. CARGO_TRANSFER: Between vessels or to shore
4. SUSPICIOUS_SPEED: >20 knots in coastal zone
...
"""
```

---

### 6. Add Historical Context (Repeat Offender)

**File**: `services/cv_agent/agent.py`

**Track vessels over time**:

```python
class MaritimeCVAgent:
    def __init__(self):
        # ... existing code ...
        self.vessel_history = {}  # Track vessel detections
    
    def analyze_frame_with_mistral(self, frame_path):
        threats = self._get_threats_from_mistral(frame_path)
        
        # Check if vessel seen before
        for threat in threats:
            vessel_desc = threat.get('description', '')
            for prev_vessel, prev_threats in self.vessel_history.items():
                if self._similar_vessel(vessel_desc, prev_vessel):
                    # Boost confidence if repeat offender
                    threat['confidence'] *= 1.2  # 20% boost
                    threat['repeat_offender'] = True
                    threat['previous_incidents'] = len(prev_threats)
        
        return threats
    
    def _similar_vessel(self, desc1, desc2):
        # Simple fuzzy match
        words1 = set(desc1.lower().split())
        words2 = set(desc2.lower().split())
        overlap = len(words1 & words2) / max(len(words1), len(words2))
        return overlap > 0.6
```

---

### 7. Multi-Frame Confirmation (Reduce False Positives)

**File**: `services/cv_agent/agent.py`

**Only alert after N consecutive frames**:

```python
class MaritimeCVAgent:
    def __init__(self):
        # ... existing code ...
        self.threat_buffer = {}  # threat_id -> [frame1, frame2, ...]
        self.confirmation_threshold = 3  # Need 3 frames
    
    def process_frame_queue(self):
        while True:
            # ... get frames ...
            threats = self.analyze_frame_with_mistral(frame_path)
            
            # Only alert threats that appear in multiple frames
            confirmed_threats = []
            for threat in threats:
                threat_id = f"{threat['threat_type']}_{threat['location']}"
                
                if threat_id not in self.threat_buffer:
                    self.threat_buffer[threat_id] = []
                
                self.threat_buffer[threat_id].append(threat)
                
                # Keep last N frames
                if len(self.threat_buffer[threat_id]) > 10:
                    self.threat_buffer[threat_id].pop(0)
                
                # Alert if threat confirmed in 3+ consecutive frames
                if len(self.threat_buffer[threat_id]) >= self.confirmation_threshold:
                    # Average confidence over frames
                    avg_conf = sum(t['confidence'] for t in self.threat_buffer[threat_id][-3:]) / 3
                    threat['confidence'] = avg_conf
                    confirmed_threats.append(threat)
            
            if confirmed_threats:
                self.publish_alert(confirmed_threats)
```

---

### 8. Integrate with External Threat Intelligence

**File**: `services/cv_agent/agent.py`

**Cross-reference with known threat database**:

```python
class MaritimeCVAgent:
    def __init__(self):
        # ... existing code ...
        self.known_smugglers = self._load_threat_intelligence()
    
    def _load_threat_intelligence(self):
        """Load from external database or API"""
        threats = {}
        try:
            # Option 1: Local JSON file
            with open('/app/known_threats.json') as f:
                threats = json.load(f)
            
            # Option 2: API call
            # response = requests.get('https://api.maritime.intel/threats')
            # threats = response.json()
        except:
            pass
        return threats
    
    def correlate_with_vessel_registry(self, threats, frame_path):
        for threat in threats:
            desc = threat.get('description', '').lower()
            
            # Check against known smugglers
            for vessel_id, vessel_intel in self.known_smugglers.items():
                if any(word in desc for word in vessel_intel['keywords']):
                    threat['known_threat'] = vessel_intel
                    threat['confidence'] *= 1.5  # Boost confidence
                    threat['severity'] = 'CRITICAL'
        
        return threats
```

**External threat feeds**:

- IMB Piracy Reporting Center: https://www.icc-ccs.org/
- UNODC Smuggling Routes
- NATO Maritime Patrol Data
- Coast Guard Notices to Mariners
- Environmental Protection Database

---

### 9. Seasonal & Weather Adjustments

**File**: `services/cv_agent/agent.py`

**Adjust threat model based on conditions**:

```python
def _build_threat_detection_prompt(self):
    from datetime import datetime
    
    month = datetime.now().month
    
    # Hurricane season (June-November)
    if month in range(6, 12):
        seasonal_focus = "1. STORM_HAZARD: Tropical disturbance, hurricane debris, storm surge"
    
    # Fishing season (varies by region)
    elif month in range(1, 4):
        seasonal_focus = "1. ILLEGAL_FISHING: Winter trawling in spawning zones"
    
    # Seasonal migration
    elif month in range(11, 2):
        seasonal_focus = "1. WHALE_STRIKE_RISK: Marine mammal presence, migration route"
    
    else:
        seasonal_focus = ""
    
    return f"""Analyze maritime scene for threats.
    
    SEASONAL FOCUS: {seasonal_focus}
    ... rest of prompt ...
    """
```

---

### 10. A/B Testing Threat Models

**File**: Create separate prompt files

**test_v1.py** (conservative):

```python
THRESHOLD = 0.75
PROMPT = """Only report HIGH-CONFIDENCE threats..."""
```

**test_v2.py** (aggressive):

```python
THRESHOLD = 0.60
PROMPT = """Report all potential threats..."""
```

**Measure**:

```bash
# Test v1 on historical data
python test_v1.py history_frames/ > results_v1.json

# Test v2 on historical data
python test_v2.py history_frames/ > results_v2.json

# Compare accuracy
python compare_models.py results_v1.json results_v2.json
```

---

## Testing Your Changes

After modifying threat detection:

### 1. Test with sample image

```bash
cd maritime_surveillance_agent
cp your_test_image.jpg uploads/test.jpg

# Monitor logs
docker compose logs -f cv_agent | grep "threat_type"
```

### 2. Test with recorded video

```bash
cp your_video.mp4 uploads/test_video.mp4
docker compose logs -f cv_agent | head -20
```

### 3. Test correlation

```bash
# Upload MAYDAY PDF
cp mayday.pdf uploads/

# Check if vessel registered
docker compose logs document_processor

# Verify correlation in next threat
docker compose logs cv_agent | grep "correlated_vessel"
```

### 4. Check email/Slack

Monitor your configured email and Slack channels for properly formatted alerts.

---

## Performance Benchmarking

### Inference Speed

Test how fast Mistral analyzes frames:

```bash
# Enter CV agent container
docker compose exec cv_agent bash

# Time a single frame analysis
time python -c "
import agent
a = agent.MaritimeCVAgent()
a.analyze_frame_with_mistral('frames/sample.jpg')
"
```

**Expected on CPU**: 2-5 seconds per frame
**Expected with GPU**: 0.5-1.5 seconds per frame

### Accuracy Metrics

For a set of 100 annotated images:

```bash
TP = correctly detected threats
FP = false alarms
TN = correctly identified safe scenes
FN = missed threats

Precision = TP / (TP + FP)          # How many alerts are correct
Recall = TP / (TP + FN)              # How many threats caught
F1 = 2 * (Precision * Recall) / (Precision + Recall)
```

---

## When to Retrain

Retrain the model if:
- False positive rate > 20%
- False negative rate (missed threats) > 10%
- New threat class emerges (e.g., new smuggling technique)
- Geographic shift (moving to new operational area)
- Vessel types change (switch from fishing to cargo monitoring)

See `THREAT_MODELS.md` for detailed threat definitions to guide your retraining efforts.

Let me know what custom threat classes or adjustments you need for your specific maritime domain!
