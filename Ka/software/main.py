#!/usr/bin/env python3
"""
AI Camera Main Application
Security + Business Analytics

Usage:
    python main.py                  # Run normally
    python main.py --init-db        # Initialize database
    python main.py --config config.json  # Use custom config
"""

import sys
import logging
import argparse
from pathlib import Path
import time
from datetime import datetime

# Add software directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import Config
from camera_handler import CameraCapture, FrameProcessor
from detector import Detector, MotionDetector
from security_module import SecurityModule
from analytics_module import AnalyticsModule
from database_handler import DatabaseHandler
import cv2
import numpy as np
from flask import Flask, jsonify, Response
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('camera.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class CameraApp:
    """Main AI Camera Application"""
    
    def __init__(self, config_file=None, api_only=False):
        logger.info("🚀 Initializing AI Camera Application")
        
        # Load configuration
        self.config = Config(config_file)
        self.api_only = api_only
        
        # Initialize components
        self.camera = CameraCapture(self.config) if not api_only else None
        self.detector = Detector(self.config)
        self.motion_detector = MotionDetector(self.config)
        self.db = DatabaseHandler(self.config.get("storage.database_path"))
        self.security = SecurityModule(self.config, self.db)
        self.analytics = AnalyticsModule(self.config, self.db)
        
        # State
        self.running = False
        self.current_frame = None
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # Flask API
        self.app = Flask(__name__)
        self._setup_api_routes()
    
    def _setup_api_routes(self):
        """Setup REST API endpoints"""
        
        @self.app.route('/api/status')
        def status():
            stats = self.db.get_statistics_summary()
            return jsonify({
                "status": "running" if self.running else "stopped",
                "timestamp": datetime.now().isoformat(),
                "frames_processed": self.fps_counter,
                "fps": f"{self.get_fps():.1f}",
                "database": stats
            })
        
        @self.app.route('/api/events')
        def get_events():
            events = self.db.get_events(limit=50)
            return jsonify(events)
        
        @self.app.route('/api/analytics')
        def get_analytics():
            analytics = self.db.get_analytics(days_back=7)
            return jsonify(analytics)
        
        @self.app.route('/api/heatmap')
        def get_heatmap():
            hm = self.analytics.get_heatmap_visualization()
            if hm is not None:
                _, buffer = cv2.imencode('.jpg', hm)
                return Response(buffer.tobytes(), mimetype='image/jpeg')
            return jsonify({"error": "Heatmap unavailable"}), 404
        
        @self.app.route('/api/live')
        def live_stream():
            return Response(self._generate_stream(), 
                          mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def _generate_stream(self):
        """Generate MJPEG stream"""
        while self.running:
            frame = self.current_frame.copy() if self.current_frame is not None else None
            if frame is not None:
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n' +
                      b'Content-Type: image/jpeg\r\n' +
                      b'Content-Length: ' + str(len(buffer)).encode() + b'\r\n\r\n' +
                      buffer.tobytes() + b'\r\n')
            time.sleep(0.033)  # ~30 FPS
    
    def get_fps(self):
        """Calculate current FPS"""
        elapsed = time.time() - self.last_fps_time
        if elapsed > 1.0:
            fps = self.fps_counter / elapsed
            self.fps_counter = 0
            self.last_fps_time = time.time()
            return fps
        return 0
    
    def initialize(self):
        """Initialize camera and models"""
        if self.api_only:
            logger.info("📡 API-Only Mode - Skipping camera initialization")
        else:
            logger.info("📷 Initializing camera...")
            if not self.camera.initialize():
                logger.error("❌ Camera initialization failed")
                return False
        
        logger.info("🤖 Loading AI models...")
        if not self.detector.load_model():
            logger.error("❌ Model loading failed")
            return False
        
        logger.info("✅ All components initialized")
        return True
    
    def process_frame(self, frame):
        """Process single frame with all modules"""
        try:
            # Motion detection
            motion_detected, motion_mag = self.motion_detector.detect_motion(frame)
            
            # Object detection
            results = self.detector.detect(frame)
            detections = self.detector.extract_detections(results) if results else []
            person_detections = self.detector.get_people_detections(detections)
            
            # Security checks
            if motion_detected and motion_mag > 10:
                self.security.generate_alert(
                    "motion_detected",
                    {
                        "severity": "medium",
                        "motion_magnitude": float(motion_mag),
                        "person_count": len(person_detections)
                    }
                )
            
            # Check for unknown faces
            if self.security.face_recognition and len(person_detections) > 0:
                faces = self.security.detect_faces(frame)
                for face in faces:
                    if not face["is_known"]:
                        self.security.generate_alert(
                            "unknown_face",
                            {
                                "severity": "critical",
                                "name": face["name"],
                                "location": face["location"]
                            }
                        )
            
            # Analytics update
            analytics_data = self.analytics.update(person_detections, frame)
            
            # Draw detections
            frame = self.detector.draw_detections(frame, detections)
            
            # Draw info overlay
            info_text = f"People: {len(person_detections)} | Motion: {motion_mag:.1f} | FPS: {self.get_fps():.1f}"
            cv2.putText(frame, info_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            self.fps_counter += 1
            return frame
        
        except Exception as e:
            logger.error(f"❌ Frame processing error: {e}")
            return frame
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            logger.error("❌ Initialization failed")
            return
        
        if not self.api_only:
            self.camera.start_capture()
        
        self.running = True
        
        # Start Flask API in background
        api_thread = threading.Thread(
            target=lambda: self.app.run(
                host=self.config.get("api.host", "0.0.0.0"),
                port=self.config.get("api.port", 5000),
                debug=False,
                use_reloader=False
            ),
            daemon=True
        )
        api_thread.start()
        logger.info("🌐 REST API started on port 5000")
        
        if self.api_only:
            logger.info("📡 API-Only Mode: Started successfully")
            logger.info("📍 Endpoints: http://localhost:5000/api/status|events|analytics|heatmap")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("⏹️  Interrupted by user")
            finally:
                self.stop()
            return
        
        logger.info("🎬 Starting main processing loop...")
        
        try:
            while self.running:
                frame = self.camera.get_frame_copy()
                
                if frame is None:
                    time.sleep(0.01)
                    continue
                
                # Process frame
                processed_frame = self.process_frame(frame)
                self.current_frame = processed_frame
                
                # Optional: Display on screen (if running on display)
                # cv2.imshow("AI Camera", processed_frame)
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
        
        except KeyboardInterrupt:
            logger.info("⏹️  Interrupted by user")
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop application gracefully"""
        logger.info("🛑 Stopping application...")
        self.running = False
        if self.camera:
            self.camera.release()
        
        # Log final statistics
        stats = self.analytics.get_statistics()
        logger.info(f"📊 Final Statistics: {stats}")
        
        logger.info("✅ Application stopped")

def main():
    parser = argparse.ArgumentParser(description="AI Camera Application")
    parser.add_argument('--config', type=str, help='Configuration file path')
    parser.add_argument('--init-db', action='store_true', help='Initialize database')
    parser.add_argument('--api-only', action='store_true', help='Run API only (no camera)')
    args = parser.parse_args()
    
    if args.init_db:
        logger.info("🗄️  Initializing database...")
        from config import Config
        cfg = Config(args.config)
        db = DatabaseHandler(cfg.get("storage.database_path"))
        logger.info("✅ Database initialized")
        return
    
    # Run main application
    app = CameraApp(args.config, api_only=args.api_only)
    app.run()

if __name__ == "__main__":
    main()
