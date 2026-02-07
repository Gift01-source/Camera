# Installation & Setup Guide

## Prerequisites

Before starting, ensure you have:
- Raspberry Pi 4 (8GB recommended) OR NVIDIA Jetson Orin Nano
- Camera module (Pi Camera v2 or Sony IMX477)
- microSD card (128GB, Class 10)
- Power supply (5V 3A for Pi, 25V 4A for Jetson)
- Ethernet or Wi-Fi connection
- Basic Linux terminal knowledge

---

## Step 1: OS Installation

### For Raspberry Pi 4

```bash
# Download Raspberry Pi Imager from official site
# Use it to flash Raspberry Pi OS (64-bit Lite) to microSD

# After booting, update system:
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-dev git
```

### For NVIDIA Jetson Orin Nano

```bash
# Download Jetson Orin Nano image from NVIDIA
# Flash using Balena Etcher

# After booting:
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-dev git
```

---

## Step 2: Enable Camera Interface

### Raspberry Pi

```bash
sudo raspi-config
# Navigate to: Interfacing Options > Camera > Enable
# Set GPU Memory: Advanced Options > Memory Split > 256
# Reboot: sudo reboot
```

Verify:
```bash
libcamera-hello --list-cameras
```

### Jetson Orin

Camera is typically already enabled. Verify:
```bash
ls -la /dev/video*
```

---

## Step 3: Clone Repository

```bash
cd ~
git clone https://github.com/Gift01-source/Camera.git
cd Camera
```

---

## Step 4: Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip setuptools wheel
pip install -r software/requirements.txt
```

**Key packages**:
- OpenCV (video capture & processing)
- YOLOv8 (object detection)
- face_recognition (face identification)
- Flask (REST API)
- SQLite3 (database)
- numpy, scipy (computation)

---

## Step 5: Download AI Models

```bash
cd software
python3 -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

# This downloads YOLOv8-Small model to ~/.cache
cd ..
```

---

## Step 6: Configure Settings

Edit configuration files in `config/` folder:

### camera_settings.json
```json
{
  "camera_index": 0,
  "resolution": [1920, 1080],
  "fps": 30,
  "flip": false,
  "rotation": 0
}
```

### detection_config.json
```json
{
  "confidence_threshold": 0.5,
  "iou_threshold": 0.45,
  "device": "cpu"
}
```

### alert_rules.json
```json
{
  "enable_alerts": true,
  "alert_email": "your.email@example.com",
  "alert_slack_webhook": "",
  "critical_classes": ["person", "weapon"]
}
```

---

## Step 7: Test Camera

```bash
cd software
python3 -c "from camera_handler import CameraCapture; cam = CameraCapture(); print('Camera OK')"
```

---

## Step 8: Run Application

### Manual Start
```bash
cd /workspaces/Camera
python3 software/main.py
```

### Background Service (Recommended)

Create systemd service:
```bash
sudo nano /etc/systemd/system/ai-camera.service
```

Paste:
```ini
[Unit]
Description=AI Camera Service
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/workspaces/Camera
Environment="PATH=/workspaces/Camera/venv/bin"
ExecStart=/workspaces/Camera/venv/bin/python3 software/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start:
```bash
sudo systemctl enable ai-camera
sudo systemctl start ai-camera
sudo systemctl status ai-camera
```

---

## Step 9: Access Dashboard

### REST API

The application starts a Flask server on `http://localhost:5000`

**Available endpoints**:
```
GET  /api/live              → Real-time video stream
GET  /api/status            → System health check
GET  /api/events            → Recent security events
GET  /api/analytics         → Daily statistics
GET  /api/heatmap           → Generated heatmap
POST /api/settings          → Update configuration
```

### Test API
```bash
curl http://localhost:5000/api/status
```

---

## Step 10: Cloud Integration (Optional)

### AWS S3 Backup

```bash
pip install boto3
```

Update `software/database_handler.py`:
```python
AWS_ACCESS_KEY = "your-access-key"
AWS_SECRET_KEY = "your-secret-key"
S3_BUCKET = "your-bucket-name"
```

---

## Performance Tuning

### Raspberry Pi

```bash
# Reduce resolution if CPU > 80%
# Modify camera_settings.json: "resolution": [1280, 720]

# Enable hardware acceleration
sudo apt install -y libjasper-dev libtiff-dev libjasper1

# Check CPU usage
top
```

### Jetson Orin

```bash
# Enable GPU for inference
# Update detection_config.json: "device": "cuda"

# Monitor GPU
nvidia-smi
```

---

## Troubleshooting

### Camera not detected
```bash
# For Raspberry Pi
libcamera-hello

# For Jetson
ls /dev/video*
```

### Model loading fails
```bash
# Check YOLO cache
rm -rf ~/.cache/ultralytics

# Redownload
python3 -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"
```

### API port already in use
```bash
# Kill process on port 5000
sudo lsof -ti:5000 | xargs kill -9

# Or change port in software/main.py
# app.run(port=5001)
```

### High CPU usage
```bash
# Reduce FPS in camera_settings.json
# Reduce resolution
# Enable model quantization
```

---

## Monitoring & Logs

```bash
# View service logs
sudo journalctl -u ai-camera -f

# Check system resources
free -h          # Memory
df -h            # Disk space
top              # CPU usage
```

---

## Database Initialization

First run automatically creates SQLite DB with schema:
```bash
python3 software/main.py --init-db
```

---

## Next Steps

1. ✅ Configure alert rules
2. ✅ Add known faces (if using face recognition)
3. ✅ Set up cloud backup
4. ✅ Build web dashboard
5. ✅ Deploy mobile app

---

**Need help?** Check [docs/TROUBLESHOOTING.md](TROUBLESHOOTING.md)
