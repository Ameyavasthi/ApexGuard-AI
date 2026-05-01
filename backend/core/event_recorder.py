import os
import cv2
import time
import queue
import threading
from collections import deque
from datetime import datetime
import config

class EventRecorder:
    def __init__(self):
        self.recordings_dir = getattr(config, 'RECORDINGS_DIR', 'recordings')
        os.makedirs(self.recordings_dir, exist_ok=True)

        self.fps = getattr(config, 'CAMERA_FPS', 20)
        self.pre_event_sec = getattr(config, 'PRE_EVENT_BUFFER_SEC', 3)
        self.post_event_sec = getattr(config, 'POST_EVENT_RECORD_SEC', 7)
        self.cooldown_sec = getattr(config, 'RECORDING_COOLDOWN_SEC', 15)

        self.buffer = deque(maxlen=self.fps * self.pre_event_sec)

        self.is_recording = False
        self._lock = threading.Lock()
        self._last_record_time = {}

        self._active_frame_queue = None

    def add_frame(self, frame):
        if frame is None: return

        if len(self.buffer) >= self.fps * self.pre_event_sec:
            self.buffer.popleft()
        self.buffer.append(frame)

        if self.is_recording and self._active_frame_queue is not None:
            try:

                self._active_frame_queue.put_nowait(frame)
            except queue.Full:
                pass  # Skip frame rather than block

    def start_recording(self, label: str) -> str:
        current_time = time.time()

        with self._lock:
            if current_time - self._last_record_time.get(label, 0) < self.cooldown_sec:
               return None
            if self.is_recording:
               return None

            self.is_recording = True
            self._last_record_time[label] = current_time

            pre_event_frames = list(self.buffer)
            self._active_frame_queue = queue.Queue(maxsize=self.fps * self.post_event_sec * 2)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{label.lower()}.webm"
        filepath = os.path.join(self.recordings_dir, filename)
        print(f"[RECORDER] Saving video: {filepath}")

        threading.Thread(
            target=self._record_video_thread,
            args=(filepath, pre_event_frames),
            daemon=True
        ).start()

        return filepath

    def _record_video_thread(self, filepath: str, pre_event_frames: list):
        out = None
        try:
            if not pre_event_frames:
                return

            height, width = pre_event_frames[0].shape[:2]

            out = None
            fourcc = cv2.VideoWriter_fourcc(*'VP80')
            candidate = cv2.VideoWriter(filepath, fourcc, float(self.fps), (width, height))
            if candidate.isOpened():
                out = candidate
                print("[RECORDER] Using codec: VP80 (.webm)")
            else:
                candidate.release()

            if out is None or not out.isOpened():
                print(f"[ERROR] VideoWriter failed with VP80 for: {filepath}")
                return

            print(f"[INFO] Recording started: {filepath}")
            print(f"[INFO] Frame shape: {pre_event_frames[0].shape}")

            for frame in pre_event_frames:
                if frame is not None:
                    out.write(frame)

            target_post_frames = self.fps * self.post_event_sec
            frames_written = 0

            while frames_written < target_post_frames:
                try:
                    frame = self._active_frame_queue.get(timeout=1.0)
                    if frame is not None:

                        if frame.shape[:2] != (height, width):
                            frame = cv2.resize(frame, (width, height))
                        out.write(frame)
                        frames_written += 1
                except queue.Empty:
                    print("[WARNING] Active queue timed out. Finalizing current video structure safely.")
                    break

            print(f"[INFO] WebM Recording finalized: {filepath}")

        except Exception as e:
            print(f"[ERROR] Catastrophic writer failure during WebM commit: {e}")
        finally:
            if out is not None:

                out.release()
            with self._lock:
                self.is_recording = False
                self._active_frame_queue = None
