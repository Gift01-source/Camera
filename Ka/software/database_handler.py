import sqlite3
import json
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class DatabaseHandler:
    """
    SQLite database handler for events, analytics, and face data
    """
    
    def __init__(self, db_path):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.initialize()
    
    def initialize(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Events table
            c.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    event_type VARCHAR(50),
                    severity VARCHAR(20),
                    person_count INTEGER,
                    confidence FLOAT,
                    metadata TEXT,
                    video_clip_path VARCHAR(255)
                )
            ''')
            
            # Analytics table
            c.execute('''
                CREATE TABLE IF NOT EXISTS analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    hour_of_day INTEGER,
                    people_count INTEGER,
                    avg_dwell_time FLOAT,
                    peak_traffic BOOLEAN,
                    conversion_rate FLOAT
                )
            ''')
            
            # Known faces table
            c.execute('''
                CREATE TABLE IF NOT EXISTS known_faces (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name VARCHAR(100) UNIQUE,
                    encoding TEXT,
                    date_added DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            c.execute('CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_analytics_timestamp ON analytics(timestamp)')
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Database initialized: {self.db_path}")
        
        except Exception as e:
            logger.error(f"❌ Database initialization error: {e}")
    
    def log_event(self, event_type, severity="medium", person_count=0, 
                  confidence=0.0, metadata=None, video_clip_path=None):
        """Log a security event"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO events (event_type, severity, person_count, confidence, metadata, video_clip_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (event_type, severity, person_count, confidence, metadata or '{}', video_clip_path))
            
            conn.commit()
            event_id = c.lastrowid
            conn.close()
            
            logger.debug(f"📝 Event logged: {event_type} (ID: {event_id})")
            return event_id
        
        except Exception as e:
            logger.error(f"❌ Event logging error: {e}")
            return None
    
    def get_events(self, limit=100, hours_back=24):
        """Retrieve recent events"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            time_threshold = datetime.now() - timedelta(hours=hours_back)
            
            c.execute('''
                SELECT * FROM events 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (time_threshold, limit))
            
            events = [dict(row) for row in c.fetchall()]
            conn.close()
            
            return events
        
        except Exception as e:
            logger.error(f"❌ Event retrieval error: {e}")
            return []
    
    def log_analytics(self, hour_of_day, people_count, avg_dwell_time, 
                     peak_traffic=False, conversion_rate=0.0):
        """Log analytics data"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''
                INSERT INTO analytics (hour_of_day, people_count, avg_dwell_time, peak_traffic, conversion_rate)
                VALUES (?, ?, ?, ?, ?)
            ''', (hour_of_day, people_count, avg_dwell_time, peak_traffic, conversion_rate))
            
            conn.commit()
            conn.close()
            logger.debug(f"📊 Analytics logged for hour {hour_of_day}")
        
        except Exception as e:
            logger.error(f"❌ Analytics logging error: {e}")
    
    def get_analytics(self, days_back=7):
        """Retrieve analytics data"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            time_threshold = datetime.now() - timedelta(days=days_back)
            
            c.execute('''
                SELECT * FROM analytics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (time_threshold,))
            
            analytics = [dict(row) for row in c.fetchall()]
            conn.close()
            
            return analytics
        
        except Exception as e:
            logger.error(f"❌ Analytics retrieval error: {e}")
            return []
    
    def add_known_face(self, name, encoding):
        """Add known face to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            encoding_json = json.dumps(encoding.tolist()) if hasattr(encoding, 'tolist') else json.dumps(encoding)
            
            c.execute('''
                INSERT OR REPLACE INTO known_faces (name, encoding)
                VALUES (?, ?)
            ''', (name, encoding_json))
            
            conn.commit()
            conn.close()
            logger.info(f"✅ Known face added: {name}")
        
        except Exception as e:
            logger.error(f"❌ Error adding known face: {e}")
    
    def get_known_faces(self):
        """Retrieve all known faces"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('SELECT * FROM known_faces')
            faces = [dict(row) for row in c.fetchall()]
            conn.close()
            
            return faces
        
        except Exception as e:
            logger.error(f"❌ Error retrieving known faces: {e}")
            return []
    
    def cleanup_old_data(self, retention_days=30):
        """Remove old events and analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            c.execute('DELETE FROM events WHERE timestamp < ?', (cutoff_date,))
            c.execute('DELETE FROM analytics WHERE timestamp < ?', (cutoff_date,))
            
            deleted_count = c.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"🗑️  Cleaned up {deleted_count} old records")
        
        except Exception as e:
            logger.error(f"❌ Cleanup error: {e}")
    
    def get_statistics_summary(self):
        """Get summary statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Total events
            c.execute('SELECT COUNT(*) FROM events')
            total_events = c.fetchone()[0]
            
            # Critical alerts count (24h)
            c.execute('''
                SELECT COUNT(*) FROM events 
                WHERE severity='critical' 
                AND timestamp > datetime('now', '-1 day')
            ''')
            critical_alerts_24h = c.fetchone()[0]
            
            # Average people count today
            c.execute('''
                SELECT AVG(people_count) FROM analytics
                WHERE date(timestamp) = date('now')
            ''')
            avg_people_today = c.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_events": total_events,
                "critical_alerts_24h": critical_alerts_24h,
                "avg_people_today": float(avg_people_today)
            }
        
        except Exception as e:
            logger.error(f"❌ Statistics summary error: {e}")
            return {}
