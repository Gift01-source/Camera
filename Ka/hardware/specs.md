# Hardware Specifications

## Recommended Build (Security + Analytics)

### 🖥️ Processing Unit

#### Option A: Raspberry Pi 4 (Budget-Friendly)
```
- Processor: ARM Cortex-A72 (1.5 GHz, 4-core)
- RAM: 4GB or 8GB
- Storage: microSD 128GB (fast, Class 10)
- Cost: ~$75-120
- Performance: ~15-30 FPS at 1080p
- Pros: Low cost, easy setup, large community
- Cons: Limited processing power
```

#### Option B: NVIDIA Jetson Orin Nano (Professional)
```
- Processor: 8-core ARM CPU + GPU
- RAM: 8GB / 12GB
- Storage: microSD 256GB (fast, Class 10)
- Cost: ~$200-300
- Performance: ~60+ FPS at 1080p, 4K capable
- Pros: Powerful, TensorRT optimization, great for real-time
- Cons: Higher cost, more power consumption
```

**Recommendation**: Start with **Raspberry Pi 4 (8GB)**, upgrade to Jetson if needed

---

### 📷 Camera Module

| Spec | Recommended |
|------|-------------|
| Sensor | Sony IMX219 or IMX477 |
| Resolution | 8MP (3280×2464) |
| Lens | 160° wide-angle or adjustable |
| Interface | CSI/MIPI (Raspberry Pi native) |
| FOV | 160° wide (surveillance preferred) |
| Cost | $15-35 |

**Options**:
- **Official Pi Camera v2**: $30, proven, 8MP
- **Arducam 12MP**: $25, better detail
- **USB Webcam**: $20, but slower

**For IR (Night Vision)**: Add separate IR module (~$20)

---

### 🔌 Power Supply

```
Raspberry Pi 4:
- USB-C 5V 3A minimum (15W)
- Battery option: 10000mAh portable (6-8 hours)
- PoE (Power over Ethernet): Optional, adds ~$30

Jetson Orin Nano:
- barrel jack 5-25V, 4A recommended
- Battery not practical (high power draw)
- PoE strongly recommended
```

---

### 💾 Storage

```
microSD Card (Primary):
- Size: 128GB Class 10 U3 (fast)
- Read Speed: 100+ MB/s
- Cost: $20-30
- Use: OS + Models

External USB SSD (Optional):
- Size: 256GB-1TB
- Speed: USB 3.0
- Cost: $30-80
- Use: Video backup / analytics data
```

---

### 🔗 Connectivity

```
Wi-Fi:
- Built-in 802.11ac (Raspberry Pi 4)
- Range: 30-50 meters
- Bandwidth: ~50-100 Mbps

Ethernet (Recommended for stable streaming):
- 1Gbps Ethernet (Raspberry Pi has native)
- Stable, reliable, recommended for 24/7 operation
- PoE: Power + Data over single cable

Bluetooth (Optional):
- For local app integration
- Range: 10-30 meters
```

---

## 📋 Bill of Materials (BoM)

### Build Option 1: Raspberry Pi 4 + Pi Camera

| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| Raspberry Pi 4 (8GB) | 1 | $75 | Main processor |
| Pi Camera v2 (8MP) | 1 | $30 | Primary camera |
| microSD 128GB (U3) | 1 | $25 | OS + models |
| USB-C 5V 3A PSU | 1 | $12 | Power supply |
| Case + Heat sink | 1 | $15 | Cooling + protection |
| USB SSD 256GB | 1 | $50 | Optional backup |
| Ethernet cable | 1 | $5 | Connectivity |
| IR Module (optional) | 1 | $20 | Night vision |
| **TOTAL** | | **$232** | **~$252 with IR** |

### Build Option 2: Jetson Orin Nano (Professional)

| Item | Qty | Cost | Notes |
|------|-----|------|-------|
| NVIDIA Jetson Orin Nano | 1 | $200 | Main processor |
| CSI Camera (Sony IMX477) | 1 | $35 | High-res camera |
| microSD 256GB (U3) | 1 | $30 | OS + models |
| Power Supply (25V 4A) | 1 | $25 | Stable power |
| Metal case (industrial) | 1 | $40 | Professional housing |
| NVMe SSD 512GB | 1 | $60 | Fast storage |
| Ethernet cable | 1 | $5 | Connectivity |
| PoE Injector (optional) | 1 | $30 | Remote power |
| **TOTAL** | | **$425** | **~$455 with PoE** |

---

## 📐 Assembly Guide

### Raspberry Pi 4 Setup

1. **Install OS**
   ```bash
   # Use Raspberry Pi Imager
   # Install: Raspberry Pi OS (Lite 64-bit)
   ```

2. **Connect Pi Camera**
   ```
   Insert CSI ribbon into Camera port (port closest to USB)
   Gently push connector down
   ```

3. **Power & Boot**
   ```bash
   sudo raspi-config
   # Enable Camera interface (Interfacing Options > Camera)
   # Enable SSH, VNC optional
   # Set GPU memory: 256MB
   ```

4. **Verify Camera**
   ```bash
   libcamera-hello --list-cameras
   ```

### Jetson Orin Nano Setup

1. **Flash OS**
   ```bash
   # Download Jetson Orin Nano image
   # Use Balena Etcher (cross-platform)
   ```

2. **Connect Camera**
   ```
   Insert camera ribbon into CSI port
   Gentle connection needed
   ```

3. **First Boot**
   ```bash
   # Follow Ubuntu setup wizard
   # Update system:
   sudo apt update && sudo apt upgrade
   ```

---

## 🌡️ Thermal Considerations

```
Cooling Options:
- Passive: Heat sink + case ventilation ✓
- Active: 30mm fan (adds $10) for continuous 24/7
- Thermal pads: Under-$5 solution

Target Temps:
- Normal: 40-50°C
- Safe: Up to 80°C
- Throttle: >85°C (performance drops)
```

---

## 🔋 Power Consumption

```
Raspberry Pi 4:
- Idle: 2-3W
- Full load: 8-15W
- With camera: +2-3W
- Battery 10000mAh: ~10-15 hours

NVIDIA Jetson Orin Nano:
- Idle: 3-5W
- Full load: 15-30W
- With camera: +3-5W
- NOT recommended for battery operation
```

---

## 📡 Network Requirements

For optimal performance:
- **Local**: Ethernet connection (0.5-1 Gbps)
- **Cloud**: 5+ Mbps upload (for cloud backup)
- **Multiple cameras**: 10+ Mbps per camera

---

## 🎁 Optional Upgrades

| Component | Cost | Benefit |
|-----------|------|---------|
| POE Switch | $50-100 | Single cable power + data |
| External HDD | $40-80 | Weeks of 24/7 recording |
| Industrial Case | $30-60 | Weatherproof, rugged |
| IR Light | $20-50 | Perfect night vision |
| Wireless battery pack | $30-50 | Mobile deployment |

---

## ✅ Checklist Before Ordering

- [ ] Choose: Raspberry Pi 4 or Jetson Orin Nano?
- [ ] Camera type: Pi Camera v2 or USB?
- [ ] Network: Ethernet or Wi-Fi?
- [ ] Storage: microSD size?
- [ ] IR needed? (Night vision)
- [ ] Budget confirmed?

---

**Next**: Follow [docs/SETUP.md](../docs/SETUP.md) for software installation
