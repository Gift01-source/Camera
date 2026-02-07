# 📱 Build APK for Smartphone - Complete Guide

Your AI Camera API is running! Now let's create a native Android APK that downloads and shows the camera status on your phone.

---

## 🚀 3 Ways to Build APK (Choose One)

### **OPTION 1: Expo + React Native (Easiest - 30 min)**

Best for: Fastest setup, no coding needed

```bash
# 1. Install Node.js if you don't have it
# Download from https://nodejs.org (LTS version)

# 2. Run the build script
cd /workspaces/Camera/Ka
bash build-apk.sh
```

This creates a React Native app that:
- ✅ Automatically shows your API status
- ✅ Displays recent events
- ✅ Auto-refreshes every 5 seconds
- ✅ Looks native on Android phone

Then:

```bash
# 3. Setup Expo
npm install -g eas-cli
eas login

# 4. Build APK
cd camera-mobile
eas build -p android --profile preview

# 5. Download APK
# Check: https://expo.dev/builds
# Scan QR code to download APK directly to phone
# Or download on computer and transfer to phone
```

✅ **APK will be ready in 5-10 minutes!**

---

### **OPTION 2: Flutter (Faster - 20 min)**

Best for: Fast native performance

```bash
# 1. Install Flutter
# https://flutter.dev/docs/get-started/install

# 2. Create Flutter project
flutter create camera_app
cd camera_app

# 3. Replace pubspec.yaml with http dependency
cat >> pubspec.yaml << 'EOF'
  http: ^1.1.0
EOF

# 4. Build APK
flutter build apk --release

# 5. APK is ready at: build/app/release/app-release.apk
```

Transfer `app-release.apk` to phone and install!

✅ **Even faster!** Pure Dart code, optimized for performance

---

### **OPTION 3: Python Kivy (If you prefer Python - 25 min)**

Best for: Python developers

```bash
# Install buildozer
pip install buildozer cython

# Create project
mkdir camera_kivy
cd camera_kivy

# Create main.py (see below)
# Then build:
buildozer android debug
```

See detailed Python code below.

---

## 🏃 **QUICKEST: Option 1 (Recommended)**

### Step-by-step:

#### **1. Check Prerequisites**
```bash
node --version    # Should show v18+
npm --version     # Should show 9+
```

If not installed, download from https://nodejs.org

#### **2. Create React Native App**
```bash
cd /workspaces/Camera/Ka
bash build-apk.sh
```

#### **3. Update API URL**

Open `camera-mobile/App.js` and find this line:
```javascript
const API_URL = 'http://10.0.2.78:5000';
```

Keep it as-is! (10.0.2.78 is your IP we found earlier)

#### **4. Build APK**
```bash
npm install -g eas-cli
eas login          # Create free Expo account

cd camera-mobile
eas build -p android --profile preview
```

#### **5. Download & Install**
- Go to https://expo.dev/builds
- Scan QR code with phone camera
- Opens download link
- Download APK
- Install on phone

✅ **That's it!** Your app is now on your phone! 🎉

---

## 📲 **What the App Shows**

Once installed, you'll see:

```
┌─────────────────────────────┐
│ 🎥 AI CAMERA               │
│ Real-time Security & Analytics
├─────────────────────────────┤
│ 📊 System Status            │
│ Status: RUNNING             │
│ FPS: 30                     │
│ Frames: 500                 │
│ Time: 14:32:15              │
├─────────────────────────────┤
│ 🚨 Recent Events            │
│ motion_detected - MEDIUM    │
│ 2026-02-07 14:30:00         │
├─────────────────────────────┤
│ 🔄 Refresh Now              │
└─────────────────────────────┘
```

---

## 🛠️ **Advanced: Use Flutter Instead**

If you prefer Flutter (faster builds):

```bash
# Install Flutter from https://flutter.dev/docs/get-started/install

flutter create camera_app
cd camera_app

# Edit lib/main.dart and add http calls
# Then build:
flutter build apk --release

# Find APK:
ls build/app/release/app-release.apk
```

---

## 🐍 **Advanced: Use Python Kivy**

If you prefer staying in Python:

```bash
pip install kivy android buildozer cython

# Create kv file for UI
# Create main.py with camera logic
# Build with buildozer:

buildozer android release
```

For complete Kivy code, see: [PYTHON_APK.md](PYTHON_APK.md)

---

## 📲 **How to Install APK on Phone**

### From Computer to Phone:
1. Download APK to computer
2. Connect phone via USB
3. Transfer APK file to phone
4. On phone: Settings → Install Unknown Apps → Allow
5. Open file manager → Find APK → Tap → Install

### Directly from Phone:
1. Scan Expo QR code from phone
2. Opens browser download
3. Download APK
4. Tap to install

---

## 🔧 **Troubleshooting**

**"App can't connect to API"**
- Check your API IP is correct in App.js
- Make sure both phone and PC are on same WiFi
- Check API is running: `curl http://10.0.2.78:5000/api/status`

**"InstallationException"**
- Phone Android version too old? (Need 5.0+)
- Install from APK directly instead

**"EAS build takes too long"**
- First build takes 15-20 min, subsequent builds 5-10 min
- Or use Flutter which builds locally (faster)

---

## 🚀 **Recommended Path for You**

### Right Now (10 min):
1. Make sure Node.js is installed
2. Run build script
3. Create Expo account
4. Start build

### Tomorrow (check back):
1. Download APK
2. Install on phone
3. See your camera status!

---

## 📱 **Next Step**

**Choose your option and run it:**

```bash
# OPTION 1 (Easiest)
cd /workspaces/Camera/Ka
bash build-apk.sh

# Then:
npm install -g eas-cli
eas login
cd camera-mobile
eas build -p android --profile preview
```

**Or tell me which option you prefer!** 🎯
