import os
import sys

# Disable OpenGL to avoid libGL.so.1 error on headless systems
os.environ['DISPLAY'] = ''
os.environ['LIBGL_ALWAYS_INDIRECT'] = '1'

# Load OpenCV without display support
import cv2
cv2.ocl.setUseOpenCL(False)

import numpy as np
from collections import deque
import threading
import time
import logging

logger = logging.getLogger(__name__)

class CameraCapture:
    """
    Handles camera capture and frame management
    Supports both Pi Camera (libcamera) and USB webcams
    """
    
    def __init__(self, config):
        self.config = config
        self.camera_index = config.get("camera.camera_index", 0)
        self.resolution = tuple(config.get("camera.resolution", [1920, 1080]))
        self.fps = config.get("camera.fps", 30)
        self.frame_buffer_size = config.get("camera.frame_buffer_size", 30)
        
        self.cap = None
        self.frame_buffer = deque(maxlen=self.frame_buffer_size)
        self.current_frame = None
        self.is_running = False
        self.capture_thread = None
        self.frame_count = 0
        self.fps_clock = time.time()
        
    def initialize(self):
        """Initialize camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open camera {self.camera_index}")
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for real-time
            
            # Read initial frame to verify
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Failed to read initial frame")
            
            # Apply transformations if needed
            frame = self._apply_transforms(frame)
            self.current_frame = frame
            self.frame_buffer.append(frame)
            
            logger.info(f"✅ Camera initialized: {self.resolution} @ {self.fps} FPS")
            return True
            
        except Exception as e:
            logger.error(f"❌ Camera initialization failed: {e}")
            return False
    
    def _apply_transforms(self, frame):
        """Apply rotation and flip transformations"""
        flip = self.config.get("camera.flip", False)
        rotation = self.config.get("camera.rotation", 0)
        
        if flip:
            frame = cv2.flip(frame, 1)
        
        if rotation == 90:
            frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        elif rotation == 180:
            frame = cv2.rotate(frame, cv2.ROTATE_180)
        elif rotation == 270:
            frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
        
        return frame
    
    def start_capture(self):
        """Start continuous frame capture in background thread"""
        if self.is_running:
            logger.warning("Capture already running")
            return
        
        self.is_running = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        logger.info("📹 Frame capture started")
    
    def _capture_loop(self):
        """Main capture loop running in background thread"""
        try:
            while self.is_running:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame")
                    continue
                
                frame = self._apply_transforms(frame)
                self.current_frame = frame
                self.frame_buffer.append(frame)
                self.frame_count += 1
                
                # Log FPS every 30 frames
                if self.frame_count % 30 == 0:
                    elapsed = time.time() - self.fps_clock
                    actual_fps = 30 / elapsed
                    logger.debug(f"Capture FPS: {actual_fps:.1f}")
                    self.fps_clock = time.time()
                
                # Maintain target FPS
                time.sleep(1.0 / self.fps)
        
        except Exception as e:
            logger.error(f"❌ Capture loop error: {e}")
            self.is_running = False
    
    def get_frame(self):
        """Get current frame"""
        return self.current_frame
    
    def get_frame_copy(self):
        """Get a copy of current frame"""
        if self.current_frame is None:
            return None
        return self.current_frame.copy()
    
    def get_buffer(self):
        """Get all buffered frames"""
        return list(self.frame_buffer)
    
    def release(self):
        """Release camera and stop capture"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        if self.cap:
            self.cap.release()
        logger.info("📷 Camera released")

class FrameProcessor:
    """
    Processes frames (resizing, normalization, etc.)
    """
    
    def __init__(self):
        pass
    
    @staticmethod
    def resize(frame, size):
        """Resize frame to target size"""
        return cv2.resize(frame, size, interpolation=cv2.INTER_LINEAR)
    
    @staticmethod
    def normalize(frame):
        """Normalize frame to 0-1 range"""
        return frame.astype(np.float32) / 255.0
    
    @staticmethod
    def denormalize(frame):
        """Denormalize frame from 0-1 range"""
        return np.clip(frame * 255, 0, 255).astype(np.uint8)
    
    @staticmethod
    def bgr_to_rgb(frame):
        """Convert BGR to RGB"""
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    @staticmethod
    def rgb_to_bgr(frame):
        """Convert RGB to BGR"""
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    @staticmethod
    def draw_fps(frame, fps_value):
        """Draw FPS on frame"""
        cv2.putText(frame, f"FPS: {fps_value:.1f}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        return frame
