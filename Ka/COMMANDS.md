# Commands Reference

## Installation & Setup

```bash
# Navigate to project
cd /workspaces/Camera

# Install/update dependencies
pip install -r software/requirements.txt --no-cache-dir

# Initialize database
python software/main.py --init-db

# Run application
python software/main.py

# Run with debug mode
python software/main.py --debug
```

---

## Testing

```bash
# Test all imports
python -c "from software.camera_handler import CameraCapture; print('✅')"
python -c "from software.detector import Detector; print('✅')"
python -c "from software.analytics_module import AnalyticsModule; print('✅')"
python -c "from software.security_module import SecurityModule; print('✅')"
python -c "from software.database_handler import DatabaseHandler; print('✅')"

# Quick database test
python -c "from software.database_handler import DatabaseHandler; db = DatabaseHandler('./data/camera.db'); print(db.get_statistics_summary())"

# Check Python version
python --version

# Check installed packages
pip list | grep -E 'opencv|torch|flask|ultralytics'
```

---

## API Testing

```bash
# Test API status (app must be running)
curl http://localhost:5000/api/status

# Get events
curl http://localhost:5000/api/events

# Get analytics
curl http://localhost:5000/api/analytics

# Get heatmap
curl http://localhost:5000/api/heatmap > heatmap.jpg

# Get live stream in browser
# Visit: http://localhost:5000/api/live
```

---

## Database Management

```bash
# View database info
sqlite3 /workspaces/Camera/data/camera.db ".tables"

# Check event count
sqlite3 /workspaces/Camera/data/camera.db "SELECT COUNT(*) FROM events;"

# Export events to CSV
sqlite3 /workspaces/Camera/data/camera.db ".mode csv" ".output events.csv" "SELECT * FROM events;" ".quit"

# Backup database
cp /workspaces/Camera/data/camera.db /workspaces/Camera/data/camera.db.backup

# Restore database
cp /workspaces/Camera/data/camera.db.backup /workspaces/Camera/data/camera.db
```

---

## File Management

```bash
# Check project structure
tree /workspaces/Camera -L 2

# Check storage usage
du -sh /workspaces/Camera/*
du -sh /workspaces/Camera/data/*

# List config files
ls -la /workspaces/Camera/config/

# View logs
tail -f camera.log

# Clear logs
> camera.log
```

---

## Git Operations

```bash
cd /workspaces/Camera

# Check status
git status

# Add all changes
git add -A

# Commit
git commit -m "feature: Update AI camera system"

# Push to remote
git push origin main

# View log
git log --oneline
```

---

## Performance & Debugging

```bash
# Monitor resource usage
watch -n 1 'ps aux | grep main.py'

# Check memory usage
free -h

# Check disk usage
df -h

# View system info
uname -a

# Check Python path
which python
python -c "import sys; print('\n'.join(sys.path))"

# Profile code
python -m cProfile -s cumtime software/main.py | head -20
```

---

## Camera & Hardware

```bash
# List video devices
ls /dev/video*

# Check camera (Raspberry Pi)
libcamera-hello --list-cameras

# Check camera (USB)
lsusb | grep -i camera

# Permissions
ls -la /dev/video*
sudo usermod -a -G video $USER
```

---

## Docker Commands (Optional)

```bash
# Build image
docker build -t ai-camera .

# Run container
docker run -p 5000:5000 --device /dev/video0 ai-camera

# Execute command in container
docker exec -it <container_id> bash

# View logs
docker logs -f <container_id>
```

---

## Configuration

```bash
# Edit camera settings
nano /workspaces/Camera/config/camera_settings.json

# Edit detection config
nano /workspaces/Camera/config/detection_config.json

# Edit alert rules
nano /workspaces/Camera/config/alert_rules.json

# Edit analytics config
nano /workspaces/Camera/config/analytics_config.json
```

---

## Service Management

```bash
# Create service
sudo nano /etc/systemd/system/ai-camera.service

# Enable service
sudo systemctl enable ai-camera

# Start service
sudo systemctl start ai-camera

# Stop service
sudo systemctl stop ai-camera

# Check status
sudo systemctl status ai-camera

# View service logs
sudo journalctl -u ai-camera -f

# Restart service
sudo systemctl restart ai-camera
```

---

## Backup & Restore

```bash
# Backup entire project
tar -czf camera_backup_$(date +%Y%m%d_%H%M%S).tar.gz /workspaces/Camera

# Restore from backup
tar -xzf camera_backup_20260207_120000.tar.gz

# Backup database only
cp /workspaces/Camera/data/camera.db ./camera_db_$(date +%Y%m%d_%H%M%S).db

# Restore database
cp ./camera_db_backup.db /workspaces/Camera/data/camera.db
```

---

## Cleanup

```bash
# Remove pycache
find /workspaces/Camera -type d -name __pycache__ -exec rm -rf {} +

# Remove .pyc files
find /workspaces/Camera -name "*.pyc" -delete

# Clear pip cache
pip cache purge

# Clear large video files
rm -rf /workspaces/Camera/videos/*

# Reset database
rm /workspaces/Camera/data/camera.db
python software/main.py --init-db
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Start app | `python software/main.py` |
| Test API | `curl http://localhost:500/api/status` |
| View logs | `tail -f camera.log` |
| Init DB | `python software/main.py --init-db` |
| Check status | `ps aux \| grep main.py` |
| Kill app | `pkill -f main.py` |
| Install deps | `pip install -r software/requirements.txt` |
| View config | `cat config/camera_settings.json` |

---

**Last Updated:** February 7, 2026
