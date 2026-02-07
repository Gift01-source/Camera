# System Architecture: AI Camera

## High-Level Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    CAMERA CAPTURE                           │
│            (Pi Camera / USB Webcam at 30 FPS)               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              FRAME BUFFER (Ring Buffer)                     │
│         Maintains last 30-60 frames in memory               │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────────────┐  ┌──────────────────────┐
│  SECURITY MODULE     │  │ ANALYTICS MODULE     │
│                      │  │                      │
│ • Face Detection     │  │ • People Counting    │
│ • Object Detection   │  │ • Heatmap Gen        │
│ • Motion Alert       │  │ • Dwell Time         │
│ • Threat Detection   │  │ • Demographics       │
│                      │  │ • Queue Management   │
└──────────┬───────────┘  └──────────┬───────────┘
           │                         │
           ├─────────────┬───────────┤
           │             │           │
           ▼             ▼           ▼
    ┌────────────┐  ┌────────────┐ ┌─────────────┐
    │   Alert    │  │  Database  │ │   Storage   │
    │  System    │  │  (SQLite)  │ │  (Local SD) │
    │   (Email   │  │            │ │  (USB SSD)  │
    │   Slack)   │  │  Events    │ │  (Cloud)    │
    └────────────┘  └────────────┘ └─────────────┘
           │             │           │
           └─────────────┼───────────┘
                         │
                         ▼
            ┌──────────────────────┐
            │   REST API Server    │
            │   (Flask/FastAPI)    │
            └──────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │Dashboard │    │Mobile App│    │Cloud Storage │
  │(Web UI)  │    │(Optional)│    │ (AWS S3)     │
  └──────────┘    └──────────┘    └──────────────┘
```

---

## Component Breakdown

### 1. **Camera Capture Layer**

```python
# software/camera_handler.py
class CameraCapture:
    - Initialize camera (Pi Camera or USB)
    - Capture frames at 30 FPS
    - Resize frames (1920x1080 or custom)
    - Handle frame rotation/flip if needed
    - Queue frames to processing pipeline
```

**Key responsibilities**:
- Maintain stable 30 FPS capture rate
- Handle camera errors gracefully
- Support multiple camera types

---

### 2. **Frame Processing Pipeline**

```
Raw Frame
    ↓
Resize (if needed)
    ↓
Normalize (0-255 to 0-1)
    ↓
Queue to AI Models
```

**Performance**: Should process at ≥ 20 FPS for real-time operation

---

### 3. **Security Module**

```python
# software/security_module.py

Functions:
├── face_detection()       # Detects faces in frame
├── face_recognition()    # Identifies known/unknown
├── object_detection()    # Weapons, suspicious items
├── motion_detection()    # Compare with previous frame
├── generate_alert()      # Email/Slack/SMS alert
├── record_incident()     # Save video clip + metadata
└── check_alert_rules()   # Apply user-defined rules
```

**Alert Types**:
- 🔴 **Critical**: Unknown person, weapon detected
- 🟠 **High**: Loitering, after-hours activity
- 🟡 **Medium**: Motion detected, unusual behavior
- 🟢 **Info**: Routine person detection

---

### 4. **Analytics Module**

```python
# software/analytics_module.py

Functions:
├── count_people()         # Count unique people per frame
├── track_movement()       # Multi-object tracking
├── generate_heatmap()     # Time-weighted density map
├── analyze_dwell_time()   # How long people stay
├── extract_demographics() # Age range, gender (optional)
├── queue_analysis()       # Queue depth & wait time
└── generate_stats()       # Daily/hourly reports
```

**Output**:
- Real-time people count
- Heatmaps (visual + data)
- Peak hours report
- Conversion metrics

---

### 5. **AI Models Layer**

```
┌─────────────────────────────────────┐
│         AI Models Used              │
├─────────────────────────────────────┤
│ YOLOv8-Small         │ 7MB   │ Fast│
│ (Object Detection)   │ 30 FPS│      │
├─────────────────────────────────────┤
│ YOLOv8-Face          │ 5MB   │ Real│
│ (Face Detection)     │ 40 FPS│ Time│
├─────────────────────────────────────┤
│ face_recognition     │ 15MB  │ ID  │
│ (Face Encoding)      │ 5 FPS │      │
├─────────────────────────────────────┤
│ Optical Flow         │ CPU   │Track│
│ (Motion Detection)   │ 60 FPS│     │
└─────────────────────────────────────┘
```

**Model Loading**:
- Load once at startup
- Cache in memory
- Use GPU/NPU if available

---

### 6. **Database Schema**

```sql
-- Events Table
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    event_type VARCHAR(50),    -- "face", "motion", "object"
    severity VARCHAR(20),      -- "critical", "high", "medium"
    person_count INTEGER,
    confidence FLOAT,
    metadata JSON,
    video_clip_path VARCHAR(255)
);

-- Analytics Table
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    hour_of_day INTEGER,
    people_count INTEGER,
    avg_dwell_time FLOAT,
    peak_traffic BOOLEAN,
    conversion_rate FLOAT
);

-- Face Recognition
CREATE TABLE known_faces (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    encoding BLOB,
    date_added DATETIME
);
```

---

### 7. **API Endpoints**

```
GET  /api/live              # Real-time stream
GET  /api/events            # Recent events
GET  /api/analytics         # Daily/hourly stats
POST /api/alert-rules       # Configure alerts
GET  /api/heatmap          # Generate heatmap
POST /api/settings         # Update config
GET  /api/status           # System health
```

---

## Data Flow: Security Scenario

```
1. Face detected in frame
                ↓
2. Extract face region & encode
                ↓
3. Compare with known faces DB
                ↓
4. Unknown person?
        ├─ YES → Generate CRITICAL alert
        │        Save frame + video clip
        │        Send Email/Slack
        │        Store in events DB
        │
        └─ NO  → Log as known person
                 Continue monitoring
```

---

## Data Flow: Analytics Scenario

```
1. Frame processed
        ↓
2. Count people: 3
        ↓
3. Track movement: Person A moved 120px right
        ↓
4. Accumulate in heatmap array
        ↓
5. Every 60 seconds:
    - Update analytics DB
    - Generate heatmap visualization
    - Calculate conversion metrics
```

---

## Performance Targets

| Metric | Target | Comment |
|--------|--------|---------|
| Frame Rate | 25-30 FPS | Real-time minimum |
| Detection Latency | <100ms | Per frame |
| Alert Response | <1 sec | From detection to alert |
| Storage (24h) | 50-100GB | 1080p continuous |
| People Count Accuracy | 95%+ | For analytics |
| False Positive Rate | <5% | Security alerts |

---

## Deployment Architecture

### Single Camera (1x Raspberry Pi)

```
Raspberry Pi 4
├── Camera module
├── AI Models (loaded in memory)
├── SQLite Database (local)
├── REST API (Flask)
└── Alert System (email/slack)
```

### Multi-Camera (Scalable)

```
┌──────────────┐
│ Central Hub  │ (Jetson)
│ (Database)   │
│ (API Server) │
└───────┬──────┘
        │
    ┌───┴────────────────┐
    │      Network       │
    │    (Ethernet)      │
    │                    │
    ▼                    ▼
Camera 1 Pi          Camera 2 Pi
(Local AI)           (Local AI)
```

---

## Security Considerations

1. **On-device Processing**: All AI inference happens locally ✅
2. **Encryption**: Face encodings stored encrypted
3. **Access Control**: API requires authentication
4. **Data Retention**: Auto-delete old events after X days
5. **Privacy**: Blur detected faces during cloud uploads (optional)

---

## Technology Stack (Detailed)

```
├── OS: Ubuntu 20.04 / Raspberry Pi OS
├── Runtime: Python 3.9+
├── AI Framework: PyTorch / TensorFlow Lite
├── Video: OpenCV 4.5+
├── Database: SQLite3
├── API: Flask or FastAPI
├── Task Scheduling: APScheduler
├── Logging: Python logging
└── Deployment: SystemD service + Docker (optional)
```

---

**Next**: Deploy with [docs/SETUP.md](SETUP.md)
