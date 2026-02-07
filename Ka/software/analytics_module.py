import numpy as np
import cv2
import logging
from collections import defaultdict
import time

logger = logging.getLogger(__name__)

class AnalyticsModule:
    """
    Handles business analytics:
    - People counting
    - Movement tracking
    - Heatmap generation
    - Statistics
    """
    
    def __init__(self, config, db_handler):
        self.config = config
        self.db = db_handler
        
        self.enable_counting = config.get("analytics.enable_people_counting", True)
        self.enable_heatmap = config.get("analytics.enable_heatmap", True)
        self.heatmap_resolution = tuple(config.get("analytics.heatmap_resolution", [640, 480]))
        self.dwell_time_threshold = config.get("analytics.dwell_time_threshold", 10)
        
        # Tracking state
        self.heatmap = np.zeros(self.heatmap_resolution, dtype=np.float32)
        self.person_tracks = {}  # Track people over time
        self.track_counter = 0
        self.frame_count = 0
        self.people_count_history = defaultdict(int)
        self.entry_times = {}  # Track entry times for dwell calculation
    
    def update(self, person_detections, frame):
        """Update analytics with new detections"""
        self.frame_count += 1
        
        # Count people
        current_count = len(person_detections)
        self.people_count_history[self.frame_count // 30] = current_count  # Every second
        
        # Update heatmap
        if self.enable_heatmap:
            self._update_heatmap(person_detections, frame)
        
        # Update tracks
        if self.enable_counting:
            self._update_tracks(person_detections)
        
        return {
            "people_count": current_count,
            "active_tracks": len(self.person_tracks),
            "average_dwell_time": self._calculate_avg_dwell_time()
        }
    
    def _update_heatmap(self, detections, frame):
        """Update heatmap with person locations"""
        try:
            frame_h, frame_w = frame.shape[:2]
            map_h, map_w = self.heatmap_resolution
            
            for det in detections:
                # Get center of detection box
                x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
                center_x = int((x1 + x2) / 2)
                center_y = int((y1 + y2) / 2)
                
                # Map to heatmap coordinates
                hm_x = int((center_x / frame_w) * map_w)
                hm_y = int((center_y / frame_h) * map_h)
                
                # Add Gaussian blob to heatmap
                cv2.circle(self.heatmap, (hm_x, hm_y), 10, 1.0, -1)
        
        except Exception as e:
            logger.error(f"❌ Heatmap update error: {e}")
    
    def _update_tracks(self, detections):
        """Track people across frames for dwell time"""
        try:
            # Simple centroid tracking
            current_centroids = {}
            
            for det in detections:
                x1, y1, x2, y2 = det["x1"], det["y1"], det["x2"], det["y2"]
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2
                current_centroids[len(current_centroids)] = (cx, cy)
            
            # Match with existing tracks
            matched_tracks = set()
            
            for track_id in list(self.person_tracks.keys()):
                old_pos = self.person_tracks[track_id]["position"]
                closest_dist = float('inf')
                closest_idx = -1
                
                for idx, pos in current_centroids.items():
                    if idx not in matched_tracks:
                        dist = np.sqrt((pos[0] - old_pos[0])**2 + (pos[1] - old_pos[1])**2)
                        if dist < closest_dist and dist < 50:  # Max distance threshold
                            closest_dist = dist
                            closest_idx = idx
                
                if closest_idx != -1:
                    self.person_tracks[track_id]["position"] = current_centroids[closest_idx]
                    self.person_tracks[track_id]["last_seen"] = time.time()
                    matched_tracks.add(closest_idx)
                else:
                    # Track lost
                    del self.person_tracks[track_id]
            
            # New tracks
            for idx, pos in current_centroids.items():
                if idx not in matched_tracks:
                    self.track_counter += 1
                    self.person_tracks[self.track_counter] = {
                        "position": pos,
                        "entry_time": time.time(),
                        "last_seen": time.time()
                    }
        
        except Exception as e:
            logger.error(f"❌ Track update error: {e}")
    
    def _calculate_avg_dwell_time(self):
        """Calculate average dwell time for active people"""
        try:
            if not self.person_tracks:
                return 0.0
            
            current_time = time.time()
            dwell_times = []
            
            for track in self.person_tracks.values():
                dwell_time = current_time - track["entry_time"]
                dwell_times.append(dwell_time)
            
            return np.mean(dwell_times) if dwell_times else 0.0
        
        except Exception as e:
            logger.error(f"❌ Dwell time calculation error: {e}")
            return 0.0
    
    def get_heatmap_visualization(self):
        """Get heatmap as visualization image"""
        try:
            # Normalize heatmap
            hm = self.heatmap.copy()
            hm = np.uint8((hm / hm.max() * 255)) if hm.max() > 0 else hm
            
            # Apply colormap
            hm_color = cv2.applyColorMap(hm, cv2.COLORMAP_JET)
            
            return hm_color
        
        except Exception as e:
            logger.error(f"❌ Heatmap visualization error: {e}")
            return None
    
    def get_statistics(self):
        """Get analytics statistics"""
        try:
            total_frames = self.frame_count
            avg_people = np.mean(list(self.people_count_history.values())) if self.people_count_history else 0
            peak_people = max(self.people_count_history.values()) if self.people_count_history else 0
            
            return {
                "total_frames": total_frames,
                "average_people_count": float(avg_people),
                "peak_people_count": int(peak_people),
                "current_tracks": len(self.person_tracks),
                "avg_dwell_time": self._calculate_avg_dwell_time(),
                "total_people_passed": self.track_counter
            }
        
        except Exception as e:
            logger.error(f"❌ Statistics calculation error: {e}")
            return {}
    
    def reset_heatmap(self):
        """Reset heatmap (e.g., daily)"""
        self.heatmap = np.zeros(self.heatmap_resolution, dtype=np.float32)
        logger.info("🔄 Heatmap reset")
    
    def reset_statistics(self):
        """Reset statistics (e.g., daily)"""
        self.people_count_history.clear()
        self.person_tracks.clear()
        self.frame_count = 0
        self.track_counter = 0
        logger.info("🔄 Statistics reset")
