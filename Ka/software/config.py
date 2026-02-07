import json
import os
from pathlib import Path

# Configuration paths
CONFIG_DIR = Path(__file__).parent.parent / "config"
MODELS_DIR = Path(__file__).parent.parent / "models"
DATABASE_PATH = Path(__file__).parent.parent / "data" / "camera.db"

# Ensure data directory exists
DATABASE_PATH.parent.mkdir(exist_ok=True)

# Default configuration
DEFAULT_CONFIG = {
    "camera": {
        "camera_index": 0,
        "resolution": [1920, 1080],
        "fps": 30,
        "flip": False,
        "rotation": 0,
        "frame_buffer_size": 30
    },
    "detection": {
        "confidence_threshold": 0.5,
        "iou_threshold": 0.45,
        "device": "cpu",  # "cpu" or "cuda"
        "model_size": "s",  # "n" (nano), "s" (small), "m" (medium)
        "inference_interval": 1  # Process every nth frame
    },
    "security": {
        "enable_face_recognition": True,
        "enable_motion_detection": True,
        "motion_threshold": 5.0,
        "record_on_alert": True,
        "recording_duration": 30,  # seconds
        "enable_alerts": True,
        "alert_email": "",
        "alert_slack_webhook": ""
    },
    "analytics": {
        "enable_people_counting": True,
        "enable_heatmap": True,
        "heatmap_resolution": [640, 480],
        "statistics_interval": 60,  # seconds
        "dwell_time_threshold": 10  # seconds
    },
    "storage": {
        "database_path": str(DATABASE_PATH),
        "video_storage_path": "./videos",
        "max_storage_gb": 500,
        "retention_days": 30,
        "cloud_backup": False,
        "aws_s3_bucket": ""
    },
    "api": {
        "host": "0.0.0.0",
        "port": 5000,
        "debug": False,
        "cors_origins": "*"
    }
}

class Config:
    def __init__(self, config_file=None):
        self.config = DEFAULT_CONFIG.copy()
        if config_file and os.path.exists(config_file):
            self.load_from_file(config_file)
    
    def load_from_file(self, config_file):
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                self._merge_config(self.config, user_config)
            print(f"✅ Config loaded from {config_file}")
        except Exception as e:
            print(f"❌ Error loading config: {e}")
    
    def _merge_config(self, base, update):
        """Recursively merge configurations"""
        for key, value in update.items():
            if isinstance(value, dict) and key in base:
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def get(self, key, default=None):
        """Get config value by dot-notation path (e.g., 'camera.resolution')"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Set config value by dot-notation path"""
        keys = key.split('.')
        cfg = self.config
        for k in keys[:-1]:
            if k not in cfg:
                cfg[k] = {}
            cfg = cfg[k]
        cfg[keys[-1]] = value
    
    def to_dict(self):
        """Return config as dictionary"""
        return self.config
    
    def save_to_file(self, config_file):
        """Save configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(config_file), exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✅ Config saved to {config_file}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")

# Initialize global config
config = Config()
