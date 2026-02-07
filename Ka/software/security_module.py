import logging
import smtplib
import json
import sqlite3
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import cv2
import os

logger = logging.getLogger(__name__)

class SecurityModule:
    """
    Handles security-related operations:
    - Face detection & recognition
    - Alert generation
    - Incident recording
    """
    
    def __init__(self, config, db_handler):
        self.config = config
        self.db = db_handler
        self.enable_face_recognition = config.get("security.enable_face_recognition", True)
        self.enable_motion_detection = config.get("security.enable_motion_detection", True)
        self.record_on_alert = config.get("security.record_on_alert", True)
        self.enable_alerts = config.get("security.enable_alerts", True)
        
        self.alert_email = config.get("security.alert_email", "")
        self.slack_webhook = config.get("security.alert_slack_webhook", "")
        
        # Attempt to load face_recognition library
        try:
            import face_recognition
            self.face_recognition = face_recognition
            self.known_faces = {}
            self._load_known_faces()
        except ImportError:
            logger.warning("⚠️  face_recognition not available")
            self.face_recognition = None
    
    def _load_known_faces(self):
        """Load known faces from database"""
        try:
            if self.db:
                known_faces = self.db.get_known_faces()
                for face in known_faces:
                    # Decode face encoding from database
                    self.known_faces[face['name']] = json.loads(face['encoding'])
                logger.info(f"✅ Loaded {len(self.known_faces)} known faces")
        except Exception as e:
            logger.error(f"❌ Error loading known faces: {e}")
    
    def detect_faces(self, frame):
        """Detect faces in frame"""
        if self.face_recognition is None:
            return []
        
        try:
            # Resize for faster processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces
            face_locations = self.face_recognition.face_locations(rgb_frame)
            face_encodings = self.face_recognition.face_encodings(rgb_frame, face_locations)
            
            faces = []
            for (top, right, bottom, left), encoding in zip(face_locations, face_encodings):
                # Scale back to original size
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                
                # Try to match with known faces
                name = self._recognize_face(encoding)
                
                faces.append({
                    "location": (top, right, bottom, left),
                    "encoding": encoding,
                    "name": name,
                    "is_known": name != "Unknown"
                })
            
            return faces
        
        except Exception as e:
            logger.error(f"❌ Face detection error: {e}")
            return []
    
    def _recognize_face(self, encoding):
        """Match face encoding with known faces"""
        if not self.known_faces:
            return "Unknown"
        
        try:
            known_encodings = list(self.known_faces.values())
            distances = self.face_recognition.face_distance(known_encodings, encoding)
            
            best_match_idx = np.argmin(distances)
            if distances[best_match_idx] < 0.6:  # Matching threshold
                return list(self.known_faces.keys())[best_match_idx]
            
            return "Unknown"
        
        except Exception as e:
            logger.error(f"❌ Face recognition error: {e}")
            return "Unknown"
    
    def generate_alert(self, alert_type, data):
        """
        Generate security alert
        
        alert_type: "unknown_face", "motion_detected", "object_detected", etc.
        data: dict with alert details
        """
        try:
            if not self.enable_alerts:
                return
            
            # Store in database
            if self.db:
                self.db.log_event(
                    event_type=alert_type,
                    severity=data.get("severity", "medium"),
                    person_count=data.get("person_count", 0),
                    confidence=data.get("confidence", 0),
                    metadata=json.dumps(data)
                )
            
            # Send notifications
            if self.alert_email:
                self._send_email_alert(alert_type, data)
            
            if self.slack_webhook:
                self._send_slack_alert(alert_type, data)
            
            logger.warning(f"🚨 Alert: {alert_type} - {data}")
        
        except Exception as e:
            logger.error(f"❌ Alert generation error: {e}")
    
    def _send_email_alert(self, alert_type, data):
        """Send email alert (requires SMTP setup)"""
        try:
            # This is a template - requires SMTP configuration
            subject = f"🚨 Security Alert: {alert_type}"
            body = f"""
            Alert Type: {alert_type}
            Severity: {data.get('severity', 'N/A')}
            Timestamp: {datetime.now()}
            Details: {json.dumps(data, indent=2)}
            """
            
            # Send email logic here
            logger.info(f"📧 Email alert would be sent: {subject}")
        
        except Exception as e:
            logger.error(f"❌ Email alert failed: {e}")
    
    def _send_slack_alert(self, alert_type, data):
        """Send Slack alert"""
        try:
            payload = {
                "text": f"🚨 **{alert_type}** Alert",
                "attachments": [{
                    "color": "danger" if data.get("severity") == "critical" else "warning",
                    "fields": [
                        {"title": "Type", "value": alert_type, "short": True},
                        {"title": "Severity", "value": data.get("severity", "N/A"), "short": True},
                        {"title": "Time", "value": str(datetime.now()), "short": False},
                        {"title": "Details", "value": json.dumps(data), "short": False}
                    ]
                }]
            }
            
            response = requests.post(self.slack_webhook, json=payload)
            if response.status_code != 200:
                logger.warning(f"⚠️  Slack alert returned: {response.status_code}")
        
        except Exception as e:
            logger.error(f"❌ Slack alert failed: {e}")
    
    def record_incident(self, frame, alert_type):
        """Record incident frame/video"""
        try:
            if not self.record_on_alert:
                return
            
            video_dir = self.config.get("storage.video_storage_path", "./videos")
            os.makedirs(video_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(video_dir, f"incident_{alert_type}_{timestamp}.jpg")
            
            cv2.imwrite(filename, frame)
            logger.info(f"📹 Incident recorded: {filename}")
            
            return filename
        
        except Exception as e:
            logger.error(f"❌ Incident recording failed: {e}")
            return None
