# API Documentation

## Endpoints

### System Status

```
GET /api/status
```

Returns system health and statistics.

**Response:**
```json
{
  "status": "running",
  "timestamp": "2026-02-07T10:30:00",
  "frames_processed": 1500,
  "fps": "28.5",
  "database": {
    "total_events": 42,
    "critical_alerts_24h": 3,
    "avg_people_today": 12.5
  }
}
```

---

### Live Stream

```
GET /api/live
```

MJPEG video stream. Can be embedded in web players.

**Usage in HTML:**
```html
<img src="http://localhost:5000/api/live" />
```

---

### Security Events

```
GET /api/events
```

Get recent security events.

**Parameters:**
- `limit` (int, default 50): Number of events
- `hours_back` (int, default 24): Look back hours

**Response:**
```json
[
  {
    "id": 1,
    "timestamp": "2026-02-07T10:25:00",
    "event_type": "unknown_face",
    "severity": "critical",
    "person_count": 1,
    "confidence": 0.98,
    "metadata": { ... }
  }
]
```

---

### Analytics Data

```
GET /api/analytics
```

Get analytics statistics.

**Response:**
```json
[
  {
    "timestamp": "2026-02-07T09:00:00",
    "hour_of_day": 9,
    "people_count": 25,
    "avg_dwell_time": 45.2,
    "peak_traffic": true,
    "conversion_rate": 0.32
  }
]
```

---

### Heatmap

```
GET /api/heatmap
```

Get heatmap visualization as JPEG image.

**Response:** JPEG image

---

### Configuration

```
POST /api/settings
```

Update system configuration.

**Request Body:**
```json
{
  "detection": {
    "confidence_threshold": 0.6
  },
  "security": {
    "enable_alerts": true
  }
}
```

---

## Error Responses

```json
{
  "error": "Error message",
  "status_code": 400
}
```

---

## Rate Limiting

No rate limiting applied. Implement in production.

---

## Authentication

Currently no authentication. Add API key authentication in production:

```python
@app.before_request
def check_api_key():
    key = request.headers.get('X-API-Key')
    if key != os.environ.get('API_KEY'):
        return jsonify({"error": "Unauthorized"}), 401
```

---

## WebSocket (Optional Enhancement)

For real-time updates, implement WebSocket:

```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    emit('response', {'data': 'Connected'})

@socketio.on('subscribe_events')
def handle_subscribe():
    # Stream events in real-time
    pass
```

Then from client:
```javascript
const socket = io('http://localhost:5000');
socket.on('event', (data) => console.log(data));
```

---

## Usage Examples

### Python Client

```python
import requests

API_URL = "http://localhost:5000"

# Get status
status = requests.get(f"{API_URL}/api/status").json()
print(status)

# Get recent events
events = requests.get(f"{API_URL}/api/events?limit=10").json()
for event in events:
    print(f"{event['event_type']}: {event['severity']}")

# Get analytics
analytics = requests.get(f"{API_URL}/api/analytics").json()
```

### JavaScript/Fetch

```javascript
const API_URL = "http://localhost:5000";

// Get status
fetch(`${API_URL}/api/status`)
  .then(r => r.json())
  .then(data => console.log(data));

// Get live stream
const img = document.querySelector('#live-stream');
img.src = `${API_URL}/api/live`;
```

### cURL

```bash
# Get status
curl http://localhost:5000/api/status

# Get events
curl http://localhost:5000/api/events?limit=20

# Get heatmap
curl http://localhost:5000/api/heatmap > heatmap.jpg
```

---

## Integration Examples

### Slack Notifications

```python
import requests

def send_slack_event(event):
    webhook = "https://hooks.slack.com/services/YOUR/WEBHOOK"
    payload = {
        "text": f"🚨 {event['event_type']}",
        "attachments": [{
            "color": "danger" if event['severity'] == "critical" else "warning",
            "fields": [
                {"title": "Severity", "value": event['severity']},
                {"title": "People", "value": event['person_count']}
            ]
        }]
    }
    requests.post(webhook, json=payload)
```

### InfluxDB Time-Series

```python
from influxdb import InfluxDBClient

client = InfluxDBClient()
events = requests.get(f"{API_URL}/api/events").json()

for event in events:
    point = {
        "measurement": "camera_events",
        "tags": {"type": event['event_type'], "severity": event['severity']},
        "fields": {"count": 1, "confidence": event['confidence']}
    }
    client.write_points([point])
```

### Grafana Dashboard

Use Grafana with InfluxDB or Prometheus to visualize metrics from the API.

---

**Version:** 1.0
**Last Updated:** February 7, 2026
