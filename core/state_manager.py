"""
core/state_manager.py — Global High-Performance Shared State
=============================================================
Centralized in-memory cache for live frames, detections, and stats.
Ensures API responses are O(1) and never block.
"""
import time
import threading
from collections import deque

class StateManager:
    def __init__(self):
        # Image State
        self.latest_frame = None       # Raw BGR frame
        self.latest_jpeg = None        # Encoded JPEG bytes
        
        # Detection State
        self.active_detections = []    # List of current detection dicts
        self.active_modules = {"animal": False, "fire": False, "weapon": False}
        
        # Analytics State (In-memory cache)
        self.stats = {
            "total": 0,
            "animals": 0,
            "fires": 0,
            "weapons": 0,
            "today": 0,
            "uptime": time.time()
        }
        self.recent_events = deque(maxlen=20) # Cache last 20 events for instant API
        
        # System Health
        self.cpu_usage = 0
        self.fps_actual = 0
        self.performance_mode = "balanced"
        
        self.state_lock = threading.Lock()

    def update_frame(self, frame, jpeg_bytes):
        with self.state_lock:
            self.latest_frame = frame
            self.latest_jpeg = jpeg_bytes

    def update_detections(self, detections):
        with self.state_lock:
            self.active_detections = detections

    def add_event(self, event_dict):
        with self.state_lock:
            self.recent_events.appendleft(event_dict)
            self.stats["total"] += 1
            etype = event_dict.get("event_type", "animal")
            if etype == "animal": self.stats["animals"] += 1
            elif etype == "fire": self.stats["fires"] += 1
            elif etype == "weapon": self.stats["weapons"] += 1
            self.stats["today"] += 1

    def get_stream_frame(self):
        with self.state_lock:
            return self.latest_jpeg

    def get_api_state(self):
        with self.state_lock:
            return {
                "detections": list(self.active_detections),
                "stats": self.stats.copy(),
                "events": list(self.recent_events),
                "modules": self.active_modules.copy(),
                "performance": {
                    "cpu": self.cpu_usage,
                    "fps": self.fps_actual,
                    "mode": self.performance_mode
                }
            }

    def seed_from_db(self):
        """Initialise stats from historical database records."""
        try:
            from api.database import SessionLocal, DetectionEvent
            db = SessionLocal()
            self.stats["total"] = db.query(DetectionEvent).count()
            self.stats["animals"] = db.query(DetectionEvent).filter(DetectionEvent.event_type == "animal").count()
            self.stats["fires"] = db.query(DetectionEvent).filter(DetectionEvent.event_type == "fire").count()
            self.stats["weapons"] = db.query(DetectionEvent).filter(DetectionEvent.event_type == "weapon").count()
            
            # Fetch last few events for the cache
            recent = db.query(DetectionEvent).order_by(DetectionEvent.timestamp.desc()).limit(20).all()
            for e in reversed(recent):
                self.recent_events.appendleft(e.to_dict())
            db.close()
        except Exception as e:
            print(f"State seed error: {e}")

# Global Singleton
state = StateManager()
