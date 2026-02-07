# 🚀 Deployment Guide

## Quick Start

### 1. API-Only Mode (No Camera Required)
```bash
cd /workspaces/Camera/Ka
python software/main.py --api-only
```
✅ **Perfect for:** Testing, CI/CD, development, cloud deployments
- ✓ REST API running on port 5000
- ✓ Database initialized
- ✓ Models loaded
- ✓ No camera needed
- ✓ Can process pre-recorded videos

### 2. Production Mode (With Camera)
```bash
cd /workspaces/Camera/Ka
python software/main.py --init-db    # First time only
python software/main.py              # Start application
```
✅ **Perfect for:** Live camera feeds on Raspberry Pi/Jetson

### 3. Custom Configuration
```bash
python software/main.py --config /path/to/config.json
```

---

## Deployment Targets

### Option A: Local Development
```bash
cd /workspaces/Camera/Ka && python software/main.py --api-only
# API available at http://localhost:5000
```

### Option B: Raspberry Pi 4 (8GB)
1. **Hardware:** RPi 4 + Pi Camera v2
2. **OS:** Raspberry Pi OS or Ubuntu 22.04
3. **Setup:**
   ```bash
   git clone https://github.com/Gift01-source/Camera.git
   cd Camera/Ka
   pip install -r software/requirements.txt
   python software/main.py --init-db
   python software/main.py
   ```
4. **Access:** `http://<pi-ip>:5000/api/status`

### Option C: NVIDIA Jetson Orin
1. **Hardware:** Jetson Orin Nano + USB camera
2. **OS:** JetPack 5.1+ (Ubuntu 22.04 base)
3. **Setup:** Same as Raspberry Pi
4. **Faster inference** with GPU acceleration

### Option D: Docker Container
```dockerfile
FROM nvidia/cuda:12.2-base-ubuntu22.04

WORKDIR /app
COPY Ka/ .
RUN pip install -r software/requirements.txt

CMD ["python", "software/main.py", "--api-only"]
```

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/status` | GET | System status, FPS, frame count |
| `/api/events` | GET | Recent security events (limit=50) |
| `/api/analytics` | GET | Analytics data (7 days history) |
| `/api/heatmap` | GET | Heatmap visualization (image/jpeg) |
| `/api/live` | GET | MJPEG live stream |

### Example Requests

```bash
# Check status
curl http://localhost:5000/api/status | jq

# Get recent events
curl http://localhost:5000/api/events?limit=10 | jq

# Get analytics
curl http://localhost:5000/api/analytics | jq

# Stream live video
curl http://localhost:5000/api/live > stream.mjpeg

# Get heatmap
curl http://localhost:5000/api/heatmap > heatmap.jpg
```

---

## System Service Setup (Systemd)

Create `/etc/systemd/system/camera-app.service`:

```ini
[Unit]
Description=AI Camera Application
After=network.target

[Service]
Type=simple
User=camera
WorkingDirectory=/home/camera/Camera/Ka
ExecStart=/usr/bin/python3 /home/camera/Camera/Ka/software/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and start:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable camera-app
sudo systemctl start camera-app
sudo systemctl status camera-app
```

---

## Monitoring & Logs

```bash
# Watch live logs
tail -f camera.log

# Check process
ps aux | grep main.py

# Monitor resource usage
top -p $(pgrep -f main.py)

# Database size
du -h data/camera.db
```

---

## Performance Tuning

| Setting | Location | Default | Notes |
|---------|----------|---------|-------|
| Model Size | `config/detection_config.json` | `yolov8s` | nano/small/medium/large |
| FPS Target | `config/camera_settings.json` | 30 | Adjust for your hardware |
| Confidence | `config/detection_config.json` | 0.5 | Lower = more detections |
| Buffer Size | `software/camera_handler.py` | 30 frames | Increase for smoother video |

---

## Troubleshooting Deployment

**Issue:** Camera not detected
```bash
# Solution: Use API-only mode
python software/main.py --api-only
```

**Issue:** No libGL.so.1
```bash
# Already fixed! We use opencv-python-headless
```

**Issue:** CUDA not detected (Jetson)
```bash
# Make sure:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

**Issue:** Out of memory
```bash
# Use smaller model:
# Edit config/detection_config.json: "model": "yolov8n"
```

**Issue:** Port 5000 already in use
```bash
# Change port in config/camera_settings.json:
# "api": {"port": 5001}
```

---

## Next Steps After Deployment

1. ✅ **Test API endpoints** - Run `curl` tests (see above)
2. ✅ **Configure alerts** - Edit `config/alert_rules.json`
3. ✅ **Add known faces** - Use database API or web interface
4. ✅ **Setup cloud backup** - Enable AWS S3 in config
5. ✅ **Create dashboard** - Consume REST API with React/Vue
6. ✅ **Monitor 24/7** - Use systemd service + log rotation

---

## Production Checklist

- [ ] Database initialized: `python software/main.py --init-db`
- [ ] API responding: `curl http://localhost:5000/api/status`
- [ ] Models downloaded: `config/yolov8*.pt` exist
- [ ] Config files in place: All files in `config/` folder
- [ ] Logs configured: `camera.log` path writable
- [ ] Camera (if needed): `/dev/video0` detected
- [ ] systemd service running: `systemctl status camera-app`
- [ ] Monitoring setup: Log rotation + disk cleanup
- [ ] Backups enabled: S3 or backup destination
- [ ] Alerts configured: Slack/email webhooks active

---

## Support

For issues, see: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

For API docs: [API.md](API.md)

For architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
