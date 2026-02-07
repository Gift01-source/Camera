# 📱 Mobile Deployment Guide

Your AI Camera API can be accessed from smartphones in multiple ways. Choose the best option for your needs.

---

## 🎯 Quick Comparison

| Option | Setup Time | Cost | Accessibility | Best For |
|--------|-----------|------|----------------|----------|
| **1. Cloud (Heroku)** | 10 min | Free-$7/mo | Public URL | Quick testing, hobby |
| **2. AWS/GCP/Azure** | 30 min | $5-50/mo | Public URL | Production, scalable |
| **3. Home Server + Port Forward** | 15 min | Free | Your network | Privacy-focused |
| **4. Ngrok Tunnel** | 5 min | Free-$5/mo | Public URL | Temporary testing |
| **5. Digital Ocean** | 20 min | $5/mo | Public URL | Simple, affordable |

---

## 🚀 **OPTION 1: Deploy to Heroku (Easiest - 10 min)**

### Step 1: Create Heroku Account
- Go to https://www.heroku.com
- Sign up (free)

### Step 2: Install Heroku CLI
```bash
curl https://cli-assets.heroku.com/install.sh | sh
heroku login
```

### Step 3: Create Procfile
```bash
cd /workspaces/Camera/Ka
cat > Procfile << 'EOF'
web: python software/main.py --api-only
EOF
```

### Step 4: Create runtime.txt
```bash
cat > runtime.txt << 'EOF'
python-3.12.0
EOF
```

### Step 5: Deploy
```bash
git add Procfile runtime.txt
git commit -m "Add Heroku deployment files"
heroku create your-app-name
git push heroku main
```

### Step 6: Access from Phone
```
https://your-app-name.herokuapp.com/api/status
```

✅ **Done!** Accessible worldwide from any phone 🎉

---

## ☁️ **OPTION 2: Deploy to AWS (Production)**

### Step 1: Prepare Docker
```bash
cd /workspaces/Camera/Ka
cat > Dockerfile << 'EOF'
FROM python:3.12-slim

WORKDIR /app
COPY software/ ./software/
COPY config/ ./config/
COPY software/requirements.txt .
RUN pip install -r requirements.txt

EXPOSE 5000
CMD ["python", "software/main.py", "--api-only"]
EOF
```

### Step 2: Push to AWS ECR
```bash
# Create ECR repository
aws ecr create-repository --repository-name camera-app

# Push image
docker build -t camera-app .
docker tag camera-app:latest YOUR_AWS_ID.dkr.ecr.us-east-1.amazonaws.com/camera-app:latest
docker push YOUR_AWS_ID.dkr.ecr.us-east-1.amazonaws.com/camera-app:latest
```

### Step 3: Launch ECS/App Runner
- Use AWS App Runner (easiest)
- Or ECS Fargate for more features

### Step 4: Get Public URL
```
https://your-app-id.awsapprunner.com/api/status
```

✅ **Cost:** ~$5-10/month for small requests

---

## 🏠 **OPTION 3: Home Server + Port Forwarding (Free)**

### Step 1: Install on Home Computer/Raspberry Pi
```bash
cd ~/Camera/Ka
python software/main.py --api-only
```

### Step 2: Port Forward on Router
1. Log into router: 192.168.1.1
2. Port Forward: External 8080 → Internal 5000
3. Get your public IP: `curl ifconfig.me`

### Step 3: Access from Phone
```
http://YOUR_PUBLIC_IP:8080/api/status
```

⚠️ **Warning:** Public IP changes. Use Dynamic DNS:
- https://www.noip.com (free subdomain)
- https://www.duckdns.org (free)

### Step 4: Setup Dynamic DNS
```bash
# Install DuckDNS client
sudo apt install curl

# Add to crontab (updates every 5 min)
*/5 * * * * curl -s https://www.duckdns.org/update?domains=yourdomain&token=YOUR_TOKEN&ip=
```

### Then access:
```
http://yourdomain.duckdns.org:8080/api/status
```

✅ **Cost:** Free (or $1/year for better domain)

---

## 🌀 **OPTION 4: Ngrok Tunnel (Fastest - 5 min)**

Perfect for immediate testing without deployment!

### Step 1: Install Ngrok
```bash
# Download from https://ngrok.com

# Or with brew
brew install ngrok
```

### Step 2: Start API
```bash
cd /workspaces/Camera/Ka
python software/main.py --api-only
```

### Step 3: Open Another Terminal
```bash
ngrok http 5000
```

### Step 4: Get Public URL
```
https://your-random-id.ngrok.io/api/status
```

### Step 5: Share with Phone
- No setup needed!
- URL changes on restart (unless paid)
- Perfect for demos

✅ **Cost:** Free (with limitations) or $5/month

---

## 📲 **Next: Create Mobile App/Dashboard**

The API is now public, but you need a way to display it on phone.

### Option A: Web Dashboard (Works on Phone Browser)
```bash
# Create simple HTML dashboard
cat > public/index.html << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>AI Camera</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        .status { background: #f0f0f0; padding: 20px; border-radius: 5px; }
        .event { background: #ffe0e0; padding: 10px; margin: 5px 0; }
    </style>
</head>
<body>
    <h1>🎥 AI Camera Status</h1>
    <div class="status" id="status">Loading...</div>
    <h2>Recent Events</h2>
    <div id="events"></div>
    <script>
        async function updateStatus() {
            const res = await fetch('/api/status');
            const data = await res.json();
            document.getElementById('status').innerHTML = `
                <p>FPS: ${data.fps}</p>
                <p>Frames: ${data.frames_processed}</p>
                <p>Status: ${data.status}</p>
            `;
        }
        updateStatus();
        setInterval(updateStatus, 5000);
    </script>
</body>
</html>
EOF
```

### Option B: React Native App
Install React Native and use `fetch()` to consume your API:
```javascript
fetch('https://your-api.com/api/status')
    .then(r => r.json())
    .then(data => setStatus(data))
```

### Option C: Flutter App
Same approach - use `http` package to call your API.

---

## ✅ **Recommended Path for You**

### For Quick Testing (5 min)
1. Use **Option 4: Ngrok Tunnel**
2. Test API in browser: `https://your-ngrok-url/api/status`
3. Access from phone browser

### For Hobby/Personal (10 min)
1. Use **Option 1: Heroku**
2. Get permanent public URL
3. Create simple web dashboard
4. Access from phone

### For Production (1-2 hours)
1. Use **Option 2: AWS / Digital Ocean**
2. Setup SSL/HTTPS
3. Create professional mobile app (React Native/Flutter)
4. Deploy to app stores

---

## 🔍 **Smartphone Access Setup**

Once API is public, access from phone:

### In Phone Browser
```
https://your-public-url/api/status
```

### Via cURL (Terminal app)
```bash
curl https://your-public-url/api/status
```

### Via Mobile App
Create app that calls:
- `/api/status` - Check system
- `/api/events` - View events
- `/api/analytics` - View stats
- `/api/live` - Stream video
- `/api/heatmap` - Get heatmap image

---

## 🛡️ **Security Considerations**

If making public, add authentication:

### Simple API Key
```python
# In main.py
if request.headers.get('X-API-Key') != 'your-secret-key':
    return {"error": "Unauthorized"}, 401
```

### OAuth2 (HTTPS recommended)
- Use framework like `flask-httpauth`
- Require login before API access

### Rate Limiting
```bash
pip install flask-limiter
```

---

## 📊 Quick Decision Tree

```
┌─ Need IMMEDIATE public access?
│  └─ Use Ngrok (5 min)
│
├─ Want PERMANENT free URL?
│  └─ Use Heroku (10 min)
│
├─ Want PRIVATE home only access?
│  └─ Use Port Forwarding (15 min)
│
├─ Want SCALABLE production?
│  └─ Use AWS/GCP (30 min)
│
└─ Want CHEAP long-term?
   └─ Use Digital Ocean ($5/mo, 20 min)
```

---

## 🚀 Start Now!

**Choose your platform:**

```bash
# Quick test with Ngrok
ngrok http 5000
# Then visit: https://your-ngrok-url/api/status on phone

# OR permanent with Heroku
heroku create your-app-name
git push heroku main
# Then visit: https://your-app-name.herokuapp.com/api/status on phone
```

---

## 📱 What to See on Phone

Once deployed, visit your API:

```
Status Page:
{
  "status": "running",
  "fps": 30.5,
  "frames_processed": 1500,
  "database": {...}
}

Events Page:
[
  {
    "type": "motion_detected",
    "severity": "medium",
    "timestamp": "2026-02-07T12:00:00"
  }
]

Analytics:
{
  "people_count": 5,
  "peak_count": 10,
  "avg_dwell_time": 45.2
}
```

---

## 📞 Support

- **Heroku issues?** See: https://devcenter.heroku.com
- **AWS issues?** See: https://aws.amazon.com/docs
- **Ngrok issues?** See: https://ngrok.com/docs
- **Port forward issues?** See your router manual
