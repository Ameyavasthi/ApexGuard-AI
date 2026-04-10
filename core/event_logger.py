"""
core/event_logger.py — Snapshot & Logging System
"""
import os
import cv2
import csv
import logging
from datetime import datetime
import config

logger = logging.getLogger(__name__)

class EventLogger:
    def __init__(self):
        self.snapshots_dir = getattr(config, 'SNAPSHOTS_DIR', 'snapshots')
        self.log_file = getattr(config, 'EVENT_LOG_FILE', 'detection_logs.csv')
        
        # Ensure directories exist
        os.makedirs(self.snapshots_dir, exist_ok=True)
        self._init_csv()

    def _init_csv(self):
        """Creates the CSV log file with headers if it doesn't already exist."""
        if not os.path.exists(self.log_file):
            with open(self.log_file, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Label", "Confidence", "Snapshot Path", "Video Path"])
                
    def log_event(self, label: str, confidence: float, frame, video_path: str = "N/A") -> str:
        """
        Captures a snapshot and logs the event details locally.
        
        Args:
            label (str): Name of detected animal.
            confidence (float): Confidence score of the detection.
            frame: OpenCV image frame corresponding to the detection.
            
        Returns:
            str: Path to the saved snapshot.
        """
        timestamp_dt = datetime.now()
        timestamp_file = timestamp_dt.strftime('%Y%m%d_%H%M%S')
        timestamp_log = timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 1. Save Snapshot immediately (Naming format: timestamp_label.jpg)
        filename = f"{timestamp_file}_{label.lower()}.jpg"
        filepath = os.path.join(self.snapshots_dir, filename)
        
        if frame is not None:
            cv2.imwrite(filepath, frame)
            logger.info(f"📸 Snapshot saved: {filepath}")
        else:
            filepath = "No Frame Provided"

        # 2. Log event metrics to CSV file
        # Store ONLY the filename (basename) — not the full path — so /snapshots/ and /video/ URLs work on any machine
        snap_basename = os.path.basename(filepath) if filepath != "No Frame Provided" else filepath
        video_basename = os.path.basename(video_path) if video_path and video_path != "N/A" else video_path
        print(f"[LOGGER] Saved snapshot: {filepath}")
        print(f"[LOGGER] Saved video basename: {video_basename}")
        try:
            with open(self.log_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    timestamp_log, 
                    label.capitalize(), 
                    round(confidence, 2), 
                    snap_basename,
                    video_basename
                ])
            logger.info(f"📝 Logged event: {label.capitalize()} | Video: {video_basename}")
        except Exception as e:
            logger.error(f"Failed to write to CSV log: {e}")
            
        return filepath
