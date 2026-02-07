# AI Models

## Overview

This directory contains AI models used by the AI Camera system.

### Models Included

#### 1. YOLOv8 (Object Detection)

**Model**: `yolov8s.pt` (YOLOv8-Small)

**Purpose**: Real-time object detection for people, vehicles, and items

**Specs:**
- Model Size: 5.3 MB
- Inference Speed: ~5-10ms per frame
- Accuracy: 96% on COCO dataset
- Classes: 80 (COCO dataset)

**Key Classes for Security/Analytics:**
- `person` - People detection
- `car`, `truck`, `bus` - Vehicles
- Possible custom classes: `weapon`, `knife`, `phone`, etc.

**Usage:**
```python
from ultralytics import YOLO

model = YOLO('yolov8s.pt')
results = model('image.jpg')
```

**Options:**
- `yolov8n.pt` - Nano (3.3MB, fastest)
- `yolov8s.pt` - Small (11.2MB, balanced) ✅ **Recommended**
- `yolov8m.pt` - Medium (26.4MB, accurate)
- `yolov8l.pt` - Large (54.3MB, slower)

---

#### 2. Face Detection & Recognition

**Libraries**: OpenCV + face_recognition

**Purpose**: Detect faces and identify known/unknown people

**Specs:**
- Face Detection: dlib CNN-based detector
- Face Encoding: ResNet-based (128D embedding)
- Accuracy: 99.38% on faces
- Speed: ~40ms per face

**Threshold:**
- Distance < 0.6: Known face
- Distance > 0.6: Unknown face

**Usage:**
```python
import face_recognition

# Load image
image = face_recognition.load_image_file("face.jpg")

# Detect faces
face_locations = face_recognition.face_locations(image)
face_encodings = face_recognition.face_encodings(image, face_locations)

# Compare with known faces
matches = face_recognition.compare_faces(known_encodings, face_encoding)
```

---

## Model Training (Optional)

### Custom Object Detection

To train a custom YOLOv8 model on your own dataset:

```bash
from ultralytics import YOLO

# Load a pretrained model
model = YOLO('yolov8s.pt')

# Train the model
results = model.train(
    data='dataset.yaml',  # Path to dataset config
    epochs=100,
    imgsz=640,
    batch=16,
    device=0  # GPU device
)
```

**Dataset Format (COCO):**
```
dataset/
├── images/
│   ├── train/
│   └── val/
├── labels/
│   ├── train/
│   └── val/
└── dataset.yaml
```

---

### Custom Face Recognition

To recognize specific people:

```python
import face_recognition
import numpy as np
from pathlib import Path

# Load known faces
known_faces = {}

for person_dir in Path('known_faces').iterdir():
    encodings = []
    for image_file in person_dir.glob('*.jpg'):
        image = face_recognition.load_image_file(image_file)
        enc = face_recognition.face_encodings(image)[0]
        encodings.append(enc)
    
    known_faces[person_dir.name] = np.mean(encodings, axis=0)

# Save to database
for name, encoding in known_faces.items():
    db.add_known_face(name, encoding)
```

---

## Model Performance

### Benchmarks (Raspberry Pi 4)

| Model | Size | FPS | Memory |
|-------|------|-----|--------|
| YOLOv8-Nano | 3.3MB | 15 FPS | 800MB |
| YOLOv8-Small | 11.2MB | 8-10 FPS | 1.2GB |
| YOLOv8-Medium | 26.4MB | 3-5 FPS | 1.5GB |

### Benchmarks (NVIDIA Jetson)

| Model | Size | FPS | Memory |
|-------|------|-----|--------|
| YOLOv8-Nano | 3.3MB | 60+ FPS | 2GB |
| YOLOv8-Small | 11.2MB | 40 FPS | 2.5GB |
| YOLOv8-Medium | 26.4MB | 25 FPS | 3GB |

---

## Model Download

Models are automatically downloaded on first use:

```python
from ultralytics import YOLO

# Auto-downloads to ~/.cache/ultralytics
model = YOLO('yolov8s.pt')
```

**Manual download:**
```bash
# Download YOLOv8-Small
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8s.pt

# Place in: ~/.cache/ultralytics/
mkdir -p ~/.cache/ultralytics
mv yolov8s.pt ~/.cache/ultralytics/
```

---

## Quantization (Speed up inference)

### TorchScript Export
```python
from ultralytics import YOLO

model = YOLO('yolov8s.pt')
model.export(format='torchscript')  # Creates yolov8s.torchscript
```

### ONNX Export (Cross-platform)
```python
model.export(format='onnx')  # Creates yolov8s.onnx
```

### TensorRT (NVIDIA optimized)
```bash
# On Jetson
model.export(format='engine')  # Creates yolov8s.engine
```

---

## Advanced: Custom Training

### Example Dataset (Weapon Detection)

```yaml
# dataset.yaml
path: /path/to/dataset
train: images/train
val: images/val

nc: 3
names: ['person', 'weapon', 'backpack']
```

### Training Script

```python
from ultralytics import YOLO

# Load base model
model = YOLO('yolov8s.pt')

# Train custom model
results = model.train(
    data='weapon_dataset.yaml',
    epochs=50,
    imgsz=640,
    batch=8,  # Reduce for Pi/Jetson
    device=0,
    patience=10,  # Early stopping
    save=True
)

# Evaluate
metrics = model.val()

# Save
model.save('custom_yolov8.pt')
```

---

## Model Licenses

- **YOLOv8**: AGPL-3.0 (open-source)
- **face_recognition**: MIT (open-source)
- **dlib**: Boost Software License (open-source)

All models are free for non-commercial use.

---

**Next**: Check [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for inference details.

**Last Updated**: February 7, 2026
