import os
import cv2
import time
import logging
import threading
import torch
import psutil
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

torch.set_num_threads(1)

import config
from core.state_manager import state
from core.video_capture import VideoCapture
from core.alert_system import AlertSystem
from core.event_logger import EventLogger
from core.event_recorder import EventRecorder

logger = logging.getLogger(__name__)

class DetectionEngine:
    def __init__(self):
        self.camera = VideoCapture()
        self.alerter = AlertSystem()
        self.recorder = EventRecorder()
        self.event_log = EventLogger()

        self.animal_detector = None
        self.fire_detector = None
        self.weapon_detector = None

        self.running = False
        self.thread = None

        self.infer_every_n = max(3, getattr(config, 'INFER_EVERY_N', 5))
        self.infer_width = getattr(config, 'INFER_WIDTH', 640)
        self.stream_quality = getattr(config, 'STREAM_QUALITY', 50)
        self.target_fps = getattr(config, 'STREAM_FPS', 10)

        self.alert_pool = ThreadPoolExecutor(max_workers=3)
        self._lock = threading.Lock()
        self.frame_count = 0
        self.last_dets = []
        self._last_fps_time = time.time()
        self._fps_counter = 0

    def start(self):
        with self._lock:
            if not self.running:
                self.running = True
                self.thread = threading.Thread(target=self._run_loop, daemon=True, name="EngineLoop")
                self.thread.start()
                logger.info("⚡ THREAT ENGINE: Started in background thread (Safe/Non-blocking).")

    def stop(self):
        with self._lock:
            self.running = False
            logger.info("🛑 THREAT ENGINE: Shutdown signaled.")

    def _run_loop(self):

        from core.animal_detector import AnimalDetector
        from core.fire_detector import FireDetector
        from core.weapon_detector import WeaponDetector

        while self.running:
            try:

                if not self.animal_detector:
                    logger.info("Engine: INITIALIZING detectors (Sequential)...")
                    self.animal_detector = AnimalDetector()
                    self.fire_detector = FireDetector()
                    self.weapon_detector = WeaponDetector()
                    logger.info("Engine: All models synchronized.")

                cam_gen = self.camera.get_frames()

                while self.running:
                    start_time = time.time()

                    if self.frame_count % 600 == 0:
                        logger.info(f"Engine Heartbeat | Frames: {self.frame_count} | CPU: {state.cpu_usage}%")

                    cpu_usage = psutil.cpu_percent(interval=None)
                    state.cpu_usage = int(cpu_usage)

                    frame = next(cam_gen, None)
                    if frame is None:
                        time.sleep(1)
                        continue

                    self.recorder.add_frame(frame)

                    h, w = frame.shape[:2]
                    scale = w / self.infer_width

                    if self.frame_count % self.infer_every_n == 0:
                        small_frame = cv2.resize(frame, (self.infer_width, int(h / scale)))
                        new_dets = []

                        try:
                            if state.active_modules.get("animal") and self.animal_detector:
                                a_dets, _ = self.animal_detector.detect(small_frame)
                                if a_dets: new_dets.extend(self._scale_dets(a_dets, scale, "animal"))
                        except Exception as e: logger.error(f"Animal detection error: {e}")

                        try:
                            if state.active_modules.get("fire") and self.fire_detector:
                                f_dets = self.fire_detector.detect(small_frame)
                                if f_dets: new_dets.extend(self._scale_dets(f_dets, scale, "fire"))
                        except Exception as e: logger.error(f"Fire detection error: {e}")

                        try:
                            if state.active_modules.get("weapon") and self.weapon_detector:
                                w_dets, _ = self.weapon_detector.detect(small_frame)
                                if w_dets: new_dets.extend(self._scale_dets(w_dets, scale, "weapon"))
                        except Exception as e: logger.error(f"Weapon detection error: {e}")

                        self.last_dets = new_dets
                        state.update_detections(new_dets)

                        if new_dets:
                            self.alert_pool.submit(self._trigger_alerts, new_dets, frame.copy())

                    annotated = self._draw_annotations(frame.copy(), self.last_dets)
                    ret, buffer = cv2.imencode('.jpg', annotated, [cv2.IMWRITE_JPEG_QUALITY, self.stream_quality])
                    if ret:
                        state.update_frame(annotated, buffer.tobytes())

                    self._fps_counter += 1
                    if time.time() - self._last_fps_time >= 1.0:
                        state.fps_actual = self._fps_counter
                        self._fps_counter = 0
                        self._last_fps_time = time.time()

                    self.frame_count += 1
                    elapsed = time.time() - start_time
                    sleep_time = max(0.015, (1.0 / self.target_fps) - elapsed)
                    time.sleep(sleep_time)

            except Exception as e:
                logger.error(f"ENGINE CRITICAL CRASH: {e}. Attempting self-healing in 5s...")
                time.sleep(5)

    def _scale_dets(self, dets, scale, etype):
        for d in dets:
            d["event_type"] = etype
            x1, y1, x2, y2 = d["bbox"]
            d["bbox"] = (int(x1 * scale), int(y1 * scale), int(x2 * scale), int(y2 * scale))
        return dets

    def _draw_annotations(self, frame, dets):

        for d in dets:
            x1, y1, x2, y2 = d["bbox"]
            label = d["label"]
            conf = d["confidence"]
            etype = d.get("event_type", "animal")

            color = (29, 158, 117) # default teal
            if etype == "fire": color = (0, 0, 255) # Red
            elif etype == "animal": color = (0, 165, 255) # Orange
            elif etype == "weapon": color = (255, 100, 0) # Blue

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, f"{label.upper()} {conf:.2f}", (x1, y1 - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        return frame

    def _trigger_alerts(self, dets, frame):
        for det in dets:
            if self.alerter.trigger_alert(det["label"]):

                logger.warning(f"Engine detected threat: {det['label']} - triggering alert infrastructure.")

                vpath = self.recorder.start_recording(det["label"])
                self.event_log.log_event(det["label"], det["confidence"], frame, vpath or "N/A")

                state.add_event({
                    "id": int(time.time()),
                    "label": det["label"],
                    "confidence": det["confidence"],
                    "event_type": det["event_type"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "snapshot_path": "temp", # real path set by logger
                    "video_path": os.path.basename(vpath) if vpath else "N/A"
                })

engine = DetectionEngine()
