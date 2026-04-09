# Maritime Threat Models - Comprehensive Guide

## What is a Threat Model?

A **threat model** is a formal framework that defines:
1. **What specific threats you want to detect** (e.g., "smuggling vessels", "wrecks", "weapons")
2. **Visual characteristics** that identify each threat (e.g., dark hulls, covered cargo, lights off)
3. **Behavioral patterns** that signal risk (e.g., evasive maneuvers, loitering in restricted zones)
4. **Confidence scoring** (how sure the model must be before alerting)
5. **Severity and recommended actions** for each threat type

## Current Threat Model (12 Classes)

Your system currently detects these maritime threats:

### 1. **DARK_VESSEL** - Severity: MEDIUM
**What it detects**: Vessels operating without navigation lights at night

**Visual indicators**:
- No visible red/green navigation lights
- Hull outline only visible from moonlight or thermal
- Running lights intentionally disabled
- Operating in darkness or reduced visibility

**Why it's suspicious**:
- Legal vessels always maintain navigation lights
- Indicates intent to avoid detection
- Common in smuggling, piracy operations

**Confidence factors**:
- Absence of navigation lights: +70%
- Operating in shipping lane at night without lights: +15%
- Course change to avoid detection: +10%
- Multiple instances: +5%

**Recommended actions**:
```
🟡 Challenge vessel on VHF
🟡 Request AIS status and intentions
🟡 Maintain surveillance
```

---

### 2. **COLLISION_RISK** - Severity: HIGH
**What it detects**: Two or more vessels on dangerous collision courses

**Visual indicators**:
- Vessels aligned on converging headings
- Closing distance rapidly
- CPA (Closest Point of Approach) < 0.5 nautical miles
- Neither vessel altering course to avoid

**Why it's critical**:
- Highest maritime accident cause
- Can indicate distress or evasion
- Potential deliberate ramming

**Confidence factors**:
- CPA < 0.3 NM: +80%
- Relative bearing change < 5°: +10%
- Speed differential > 5 knots: +5%
- One vessel not responding to hails: +5%

**Recommended actions**:
```
🟡 Issue collision warning to both vessels
🟡 Monitor CPA and vessel speeds
🟡 Prepare emergency coordination if needed
```

---

### 3. **VESSEL_GATHERING** - Severity: MEDIUM
**What it detects**: Multiple vessels in unusual clustering or rendezvous

**Visual indicators**:
- 3+ vessels in close proximity (< 500m)
- Coordinated holding position
- Transferring cargo between vessels
- Formation maneuvering

**Why it's suspicious**:
- Indicates planned meetup (often illegal cargo transfer)
- Anchoring in prohibited zones
- May precede smuggling or piracy

**Confidence factors**:
- Number of vessels in cluster: +10% per vessel (capped at 30%)
- Time holding formation: +15% (per 10 minutes)
- Location in restricted zone: +20%
- AIS signals disabled on one or more: +25%

**Recommended actions**:
```
🟡 Monitor for coordinated activity
🟡 Log all vessel identities and positions
🟡 Check for known smuggling routes
🟡 Request explanation of gathering
```

---

### 4. **SMUGGLING_VESSEL** - Severity: HIGH
**What it detects**: Small boats exhibiting smuggling indicators

**Visual indicators**:
- Small fast craft (20-50ft)
- Low freeboard (sitting low in water)
- Covered cargo areas
- Running at high speed
- Operating at night
- No visible cargo handling equipment
- Multiple trips to/from shore

**Why it's suspicious**:
- Vessel profile matches known smuggling craft
- Operational patterns indicate contraband
- Avoidance of ports and inspection

**Confidence factors**:
- Hull type match: +40%
- Operating at night: +20%
- High speed in coastal waters: +15%
- No cargo documentation visible: +15%
- Previous incidents database match: +10%

**Recommended actions**:
```
🟡 Flag vessel for inspection
🟡 Request vessel boarding authorization
🟡 Log cargo and destination
```

---

### 5. **WEAPONS** - Severity: CRITICAL
**What it detects**: Mounted firearms, missile launchers, or military hardware

**Visual indicators**:
- Visible gun turrets or mounts
- Missile launcher systems
- Armed personnel on deck
- Combat configuration
- Weapon barrels visible
- Military-grade radar systems

**Why it's critical**:
- Immediate life safety threat
- Indicates military or pirate vessel
- Potential boarding threat

**Confidence factors**:
- Weapon system identification: +85%
- Active aiming behavior: +10%
- Crewed weapons station: +5%

**Recommended actions**:
```
🔴 ESCALATE TO COMMAND - Armed threat confirmed
🔴 Scramble response vessel immediately
🔴 Contact naval authorities for support
```

---

### 6. **MILITARY_VESSEL** - Severity: MEDIUM
**What it detects**: Warships, naval vessels, combat aircraft carriers

**Visual indicators**:
- Classified hull design
- Military paint scheme
- Radar systems visible
- Military personnel
- Combat configuration
- National flag markings
- Helicopter deck or hanger

**Why it's flagged**:
- Requires tracking and reporting
- Potential international incident
- May indicate regional tension

**Confidence factors**:
- Hull classification match: +60%
- Military radar signature: +20%
- Official vessel registry: +15%
- Escort vessels present: +5%

**Recommended actions**:
```
🟡 Monitor vessel movements closely
🟡 Log vessel details and trajectory
🟡 Maintain safe distance
```

---

### 7. **PIRATES** - Severity: CRITICAL
**What it detects**: Hostile boarding attempts, armed attack patterns

**Visual indicators**:
- Fast approach vectors
- Armed personnel
- Boarding equipment (grapples, ladders)
- Weapons directed at target vessel
- Aggressive maneuvering
- Crew actions indicate threat

**Why it's critical**:
- Active threat to maritime commerce
- Life safety emergency
- Criminal act in progress

**Confidence factors**:
- Rapid closing on merchant vessel: +70%
- Armed personnel visible: +20%
- Boarding preparation observed: +5%
- Distress call received: +5%

**Recommended actions**:
```
🔴 ESCALATE TO COMMAND - Armed threat confirmed
🔴 Scramble response vessel immediately
🔴 Contact naval authorities for support
```

---

### 8. **WRECK** - Severity: HIGH
**What it detects**: Sunken vessels, floating debris, capsized boats, shipwrecks

**Visual indicators**:
- Upside-down hull visible
- Floating debris field
- Oil slick around wreck
- Vessel partially submerged
- Debris trail on surface
- Rescue operations ongoing

**Why it's critical**:
- Indicates maritime disaster
- Potential rescue situation
- Navigation hazard
- Environmental cleanup required

**Confidence factors**:
- Hull identification: +75%
- Debris field extent: +10%
- Oil spill presence: +10%
- Vessel reports matching: +5%

**Recommended actions**:
```
🔴 EMERGENCY - Dispatch rescue vessels
🔴 Alert coast guard and emergency services
🟡 Initiate search and rescue protocols
```

---

### 9. **FIRE** - Severity: CRITICAL
**What it detects**: Active fires, heavy smoke, burning vessels

**Visual indicators**:
- Visible flames on deck
- Heavy black/white smoke
- Heat signature on thermal
- Vessel listing or sinking
- Crew abandonment activity
- Emergency flares deployed

**Why it's critical**:
- Life-threatening emergency
- Total loss risk
- Environmental hazard
- Requires immediate response

**Confidence factors**:
- Visible flames: +90%
- Smoke visible: +70%
- Vessel movement erratic: +15%
- Distress call active: +5%

**Recommended actions**:
```
🔴 EMERGENCY - Dispatch rescue vessels
🔴 Alert coast guard and emergency services
🟡 Initiate search and rescue protocols
```

---

### 10. **OIL_SPILL** - Severity: HIGH
**What it detects**: Surface oil slicks, pollution, environmental hazards

**Visual indicators**:
- Rainbow sheen on water surface
- Dark discoloration spreading
- Oil slick extent visible
- Weather-related appearance
- Thick surface film
- Floating oil balls

**Why it's serious**:
- Environmental damage
- Ecosystem impact
- Navigation hazard (slippery surface)
- Violation of maritime pollution laws (MARPOL)

**Confidence factors**:
- Sheen detection: +65%
- Slick extent > 1 hectare: +20%
- Wind direction matching source: +10%
- Reported spill matching: +5%

**Recommended actions**:
```
🟡 Alert environmental protection agency
🟡 Dispatch pollution response team
🟡 Establish containment zone
```

---

### 11. **UNKNOWN_AIS** - Severity: MEDIUM
**What it detects**: Vessels with missing or disabled AIS signals

**Visual indicators**:
- AIS transponder offline
- Question mark indicator in tracking systems
- No MMSI number visible
- Unresponsive to vessel identification queries
- Matching silhouette in multiple feeds
- Manual tracking required

**Why it's suspicious**:
- AIS disabled intentionally
- Avoids automated tracking
- Indicates criminal intent (smuggling, piracy)
- Makes prosecution difficult

**Confidence factors**:
- Confirmed AIS offline: +75%
- Visual ID matches known vessel: +15%
- Previous smuggling record: +10%

**Recommended actions**:
```
🟡 Attempt to identify vessel visually
🟡 Request AIS activation
🟡 Cross-reference visual characteristics
```

---

### 12. **ENDANGERED_WATERS** - Severity: MEDIUM
**What it detects**: Vessels in restricted zones, protected waters, hazardous areas

**Visual indicators**:
- Operating in marked restricted zone
- Near marine sanctuary
- Shallow water navigation
- Proximity to environmental protection zone
- Transit lane violation
- Coordinates indicate prohibited area

**Why it's flagged**:
- Regulatory violation
- Environmental risk
- May indicate illegal dumping/fishing
- Potential grounding risk

**Confidence factors**:
- GPS coordinates in prohibited zone: +70%
- Depth below safe threshold: +15%
- No permit visible: +10%
- Previous violations: +5%

**Recommended actions**:
```
🟢 Monitor for potential violations
🟢 Log proximity to restricted zone
🟢 Request vessel's purpose and permit
```

---

## Customizing Your Threat Model

### Adding a New Threat Class

To add a new threat (e.g., "ILLEGAL_FISHING"):

**1. Update CV agent prompt** (`services/cv_agent/agent.py`):

```python
def _build_threat_detection_prompt(self):
    return """...
    13. ILLEGAL_FISHING: Trawler nets in protected zone, bottom-dragging in sanctuary, protected species catch
    ...
    """
```

**2. Add threat category to THREAT_CLASSES**:

```python
THREAT_CLASSES = {
    "illegal_fishing": {
        "keywords": ["trawler", "bottom-dragging", "protected zone", "sanctuary"],
        "severity": 0.7
    },
    # ... other threats
}
```

**3. Update action generation** (`_generate_actions()`):

```python
elif "illegal_fishing" in threat_type:
    actions.add("🟡 Alert fisheries enforcement")
    actions.add("🟡 Request catch documentation")
    actions.add("🟡 Initiate boarding inspection")
```

**4. Update dashboard** (`dashboard.html`):

Add to threat breakdown and threat color mapping.

### Adjusting Confidence Thresholds

In `docker-compose.yml`:

```yaml
THREAT_CONFIDENCE_THRESHOLD=0.6  # Alert on 60%+ confidence
```

- **0.4-0.5**: Very sensitive, high false positives
- **0.6-0.7**: Balanced (recommended)
- **0.75-0.85**: Conservative, may miss threats
- **0.9+**: Critical only, may not catch evolving threats

### Fine-tuning Severity Mapping

In `_calculate_threat_level()`:

```python
def _calculate_threat_level(self, threats):
    if not threats:
        return "GREEN"
    
    # Check for CRITICAL threats first
    critical_threats = ["WEAPONS", "PIRATE", "FIRE", "WRECK"]
    if any(t.get("threat_type") in critical_threats for t in threats):
        return "RED"
    
    max_severity = max([t.get("confidence", 0) for t in threats], default=0)
    if max_severity >= 0.9:
        return "RED"
    elif max_severity >= 0.75:
        return "YELLOW"
    else:
        return "ORANGE"
```

---

## Training Your Model on Custom Scenarios

### Scenario 1: Suspected Drug Smuggling

```json
{
  "threat_type": "SMUGGLING_VESSEL",
  "confidence": 0.92,
  "location": "off Cartagena coast",
  "description": "25m speedboat, low freeboard, covered cargo area, no lights, high speed toward beach landing zone at 03:00 local time. Previous intelligence links vessel to known trafficking organization.",
  "severity": "HIGH",
  "coordinates_frame": "45%, 60%"
}
```

### Scenario 2: Search and Rescue

```json
{
  "threat_type": "WRECK",
  "confidence": 0.88,
  "location": "center field",
  "description": "Capsized fishing vessel, crew visible on hull, oil slick spreading, lifeboat deployed with 8 survivors visible. Vessel identified as 'Lucky Star' MMSI 123456789 - matches MAYDAY received 15 minutes ago.",
  "severity": "CRITICAL",
  "coordinates_frame": "50%, 50%"
}
```

### Scenario 3: Environmental Violation

```json
{
  "threat_type": "OIL_SPILL",
  "confidence": 0.85,
  "location": "port side of channel",
  "description": "Rainbow sheen visible over 3+ hectare area, vessel identified as tanker with AIS disabled, estimated 500 barrels released, prevailing current carries slick toward marine sanctuary 8nm away.",
  "severity": "HIGH",
  "coordinates_frame": "30%, 40%"
}
```

---

## Correlation with Document Intelligence

When a MAYDAY PDF arrives:

```
MAYDAY RECEIVED:
- Vessel: MV Northern Star
- MMSI: 987654321
- Position: 40.12°N 73.95°W
- Status: SINKING - ENGINE ROOM FIRE
- Crew: 22
```

Your CV agent:

1. **Registers vessel data** in `vessel_registry`
2. **Searches live feeds** for visual matches within 5nm radius
3. **Scores visual similarity**:
   - Size match: +30%
   - Color/markings: +20%
   - Location proximity: +25%
   - Behavior (sinking, fire visible): +25%
4. **If match found** (total >70%):
   - Escalates to **PRIORITY/RED**
   - Includes vessel info in SITREP
   - Marks as **CORRELATED_VESSEL**
   - Triggers **LIFE SAFETY** protocol

---

## Performance Tuning

### Reducing False Positives

1. **Increase confidence threshold**: `0.75` instead of `0.6`
2. **Require multi-frame confirmation**: Alert only if same threat appears in 3+ consecutive frames
3. **Geographic filtering**: Skip known safe zones
4. **Time-of-day filtering**: Adjust thresholds for night operations

### Reducing False Negatives (Missing Real Threats)

1. **Decrease confidence threshold**: `0.5` instead of `0.7`
2. **Add seasonal models**: Different threat patterns in hurricane season, fishing season, etc.
3. **Enable correlation always**: Even low-confidence threats correlate with MAYDAYs
4. **Historical context**: Remember vessel profiles over time

---

## Next Steps

1. **Deploy your system** with current 12-threat model
2. **Collect 100+ threat samples** (photos + annotations)
3. **Fine-tune prompts** based on false positives/negatives
4. **Add domain-specific threats** (e.g., illegal fishing in your AOR)
5. **Retrain on Mistral 7B locally** with your maritime scenarios

Let me know what threats are most critical for your area of operations!
