# Troubleshooting Guide

## Common Issues & Solutions

### Camera Issues

#### Problem: Camera not detected

**Error:** `Failed to open camera 0`

**Solutions:**
```bash
# For Raspberry Pi - check if camera is enabled
libcamera-hello --list-cameras

# If nothing shows:
sudo raspi-config
# Go to Interfacing Options > Camera > Enable

# Or check /dev/video*
ls /dev/video*

# If mmal_vc_component_create failed:
# This means legacy camera mode is still active
grep "start_x=1" /boot/config.txt
# Update to libcamera in /boot/config.txt
```

**.For Jetson:**
```bash
ls /dev/video*
# Try v4l2-ctl
v4l2-ctl --list-devices
```

---

#### Problem: Low FPS (< 15 FPS)

**Causes:** High CPU usage, resolution too high, model too large

**Solutions:**
```bash
# 1. Reduce resolution in config/camera_settings.json
"resolution": [1280, 720]  // Instead of 1920x1080

# 2. Reduce model size
"model_size": "n"  // Nano instead of Small

# 3. Check CPU usage
top
ps aux | grep main.py

# 4. Disable unnecessary features
"enable_face_recognition": false
"enable_heatmap": false
```

---

#### Problem: Camera feed frozen or lagging

**Solutions:**
```python
# In camera_handler.py, reduce buffer size:
self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

# Reduce FPS in settings:
"fps": 15
```

---

### AI Model Issues

#### Problem: Model loading fails

**Error:** `Failed to load model`

**Solutions:**
```bash
# Clear model cache
rm -rf ~/.cache/ultralytics
pip cache purge

# Try downloading again
python3 -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

# Check internet connection
ping 8.8.8.8

# For Jetson, ensure PyTorch is installed for ARM
pip install torch torchvision -f https://download.pytorch.org/whl/torch_stable.html
```

---

#### Problem: Very slow inference (> 1 second per frame)

**Solutions:**
```bash
# 1. Use smaller model
"model_size": "n"  # Nano = fastest

# 2. Enable GPU/NPU
"device": "cuda"  # For NVIDIA

# 3. Reduce inference interval (skip frames)
"inference_interval": 2  # Process every 2nd frame

# 4. Reduce resolution before inference
```

---

#### Problem: Out of Memory (OOM)

**Error:** `CUDA out of memory` or `malloc failed`

**Solutions - Raspberry Pi:**
```bash
# Check memory
free -h

# Increase GPU memory
sudo raspi-config
# Advanced Options > Memory Split > 256MB

# Reboot
sudo reboot
```

**Solutions - Jetson:**
```bash
# Check VRAM
nvidia-smi

# Use smaller model
"model_size": "n"

# Reduce batch processing
```

---

### Database Issues

#### Problem: Database locked error

**Error:** `database is locked`

**Solutions:**
```bash
# 1. Check if multiple instances are running
ps aux | grep main.py

# 2. Build database index
python3 software/main.py --init-db

# 3. Rebuild database
rm ~/Camera/data/camera.db
python3 software/main.py --init-db
```

---

#### Problem: Database growing too large

**Solutions:**
```bash
# 1. Check database size
du -sh ~/Camera/data/camera.db

# 2. Enable auto-cleanup in config
"retention_days": 30

# 3. Manually cleanup
# Edit main.py to call:
db.cleanup_old_data(retention_days=30)

# 4. Archive old data
sqlite3 camera.db "SELECT * FROM events WHERE date(timestamp) < date('now', '-90 days')" > archived_events.csv
```

---

### API Issues

#### Problem: API port already in use

**Error:** `Address already in use`

**Solutions:**
```bash
# 1. Kill existing process
lsof -ti:5000 | xargs kill -9

# 2. Change port in config/camera_settings.json
"api": {
  "port": 5001
}

# 3. Check what's using the port
netstat -tulpn | grep 5000
```

---

#### Problem: Cannot access API from other machine

**Error:** `Connection refused`

**Solutions:**
```bash
# 1. Ensure API is listening on 0.0.0.0
"api": {
  "host": "0.0.0.0",
  "port": 5000
}

# 2. Check firewall
sudo ufw status
sudo ufw allow 5000

# 3. Find device IP
hostname -I

# 4. Try from remote:
curl http://192.168.1.100:5000/api/status
```

---

#### Problem: CORS errors in web dashboard

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solutions - Add CORS headers:**
```python
# In main.py
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"])  # Or specify domains
```

---

### Face Recognition Issues

#### Problem: Face recognition not working

**Error:** `Module not found`

**Solutions:**
```bash
# Install face_recognition and dlib
pip install face_recognition dlib

# On Raspberry Pi (may take time)
pip install face_recognition --no-cache-dir

# Add known faces to database
python3
from software.database_handler import DatabaseHandler
import json
db = DatabaseHandler("./data/camera.db")
# Encode face first, then:
db.add_known_face("John", encoding_array)
```

---

#### Problem: Too many false positives (detecting non-faces)

**Solution:** Increase face detection sensitivity

```python
# In security_module.py, adjust matching threshold:
if distances[best_match_idx] < 0.5:  # Lower = stricter
    return name
```

---

### Performance & Optimization

#### Problem: High CPU usage (>90%)

**Analysis:**
```bash
# See which process uses most CPU
top -p $(pgrep -f main.py)

# Profile the code
python3 -m cProfile -s cumtime software/main.py | head -30
```

**Solutions:**
- Reduce resolution
- Use smaller model
- Disable face recognition
- Process every 2-3rd frame instead of every frame

---

#### Problem: Memory leak (RAM keeps growing)

**Solutions:**
```bash
# Monitor memory
free -h && sleep 60 && free -h

# Check for circular references
import gc
gc.collect()

# Restart service periodically
# Add to crontab:
0 2 * * * systemctl restart ai-camera  # Restart at 2 AM
```

---

### Logging & Debugging

#### Enable debug logging

```python
# In main.py
logging.basicConfig(level=logging.DEBUG)

# Run and check logs
tail -f camera.log
```

#### Get system information

```bash
# Camera info
libcamera-hello --info

# System info
uname -a
lsb_release -a
df -h
```

---

## Getting Help

### Check logs first
```bash
tail -50 camera.log
dmesg | tail -20
```

### Enable verbose mode
```bash
python3 software/main.py --debug
```

### Test components individually
```python
# Test camera
python3 -c "from camera_handler import *; CameraCapture({}).initialize()"

# Test detector
python3 -c "from detector import *; Detector({}).load_model()"

# Test API
curl -v http://localhost:5000/api/status
```

---

**Last Updated:** February 7, 2026
