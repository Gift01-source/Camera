import numpy as np
import cv2
from ultralytics import YOLO
import logging
import time

logger = logging.getLogger(__name__)

class Detector:
    """
    AI object detector using YOLOv8
    Handles person, object, and threat detection
    """
    
    def __init__(self, config):
        self.config = config
        self.model = None
        self.device = config.get("detection.device", "cpu")
        self.model_size = config.get("detection.model_size", "s")
        self.confidence_threshold = config.get("detection.confidence_threshold", 0.5)
        self.iou_threshold = config.get("detection.iou_threshold", 0.45)
        
        self.inference_count = 0
        self.last_inference_time = 0
        
    def load_model(self):
        """Load YOLO model"""
        try:
            model_name = f"yolov8{self.model_size}.pt"
            self.model = YOLO(model_name)
            self.model.to(self.device)
            logger.info(f"✅ YOLO model loaded: {model_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            return False
    
    def detect(self, frame):
        """
        Detect objects in frame
        Returns: results object with detections
        """
        try:
            if self.model is None:
                return None
            
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                device=self.device,
                verbose=False
            )
            
            self.inference_count += 1
            self.last_inference_time = time.time()
            
            return results[0] if results else None
        
        except Exception as e:
            logger.error(f"❌ Detection error: {e}")
            return None
    
    def extract_detections(self, results):
        """
        Extract detection information
        Returns: list of dict with class_name, confidence, box
        """
        if results is None:
            return []
        
        detections = []
        for box in results.boxes:
            detection = {
                "class_id": int(box.cls),
                "class_name": self.model.names[int(box.cls)],
                "confidence": float(box.conf),
                "x1": int(box.xyxy[0][0]),
                "y1": int(box.xyxy[0][1]),
                "x2": int(box.xyxy[0][2]),
                "y2": int(box.xyxy[0][3])
            }
            detections.append(detection)
        
        return detections
    
    def draw_detections(self, frame, detections):
        """Draw detection boxes on frame"""
        for det in detections:
            x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
            conf = det["confidence"]
            class_name = det["class_name"]
            
            # Color based on confidence
            color = (0, 255, 0) if conf > 0.7 else (0, 165, 255)
            
            # Draw box
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            
            # Draw label
            label = f"{class_name} {conf:.2f}"
            cv2.putText(frame, label, (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        return frame
    
    def get_people_detections(self, detections):
        """Filter detections to get only people"""
        return [d for d in detections if d["class_name"] == "person"]
    
    def get_vehicle_detections(self, detections):
        """Filter detections to get vehicles"""
        vehicle_classes = ["car", "truck", "bus", "motorcycle", "bicycle"]
        return [d for d in detections if d["class_name"] in vehicle_classes]


class MotionDetector:
    """
    Detect motion between frames using optical flow
    """
    
    def __init__(self, config):
        self.config = config
        self.motion_threshold = config.get("security.motion_threshold", 5.0)
        self.prev_frame = None
    
    def detect_motion(self, frame):
        """
        Detect motion using frame difference
        Returns: motion_detected (bool), motion_magnitude (float)
        """
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            if self.prev_frame is None:
                self.prev_frame = gray
                return False, 0.0
            
            # Calculate difference
            diff = cv2.absdiff(gray, self.prev_frame)
            _, thresh = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
            
            # Calculate motion magnitude
            motion_magnitude = np.sum(thresh) / (255.0 * thresh.size) * 100
            motion_detected = motion_magnitude > self.motion_threshold
            
            self.prev_frame = gray
            
            return motion_detected, motion_magnitude
        
        except Exception as e:
            logger.error(f"❌ Motion detection error: {e}")
            return False, 0.0

