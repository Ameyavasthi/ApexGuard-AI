import cv2
import time
import logging
import config

logger = logging.getLogger(__name__)

class VideoCapture:
    def __init__(self, source: str = None):
        self.source_name = source or config.ACTIVE_CAMERA
        self.source_id   = config.WEBCAM_SOURCE if self.source_name == "webcam" else config.IP_CAMERA_SOURCE
        self.cap = None
        self._connect()

    def _connect(self):
        logger.info(f"Connecting to camera: {self.source_name}")
        self.cap = cv2.VideoCapture(self.source_id)
        if not self.cap.isOpened():
            logger.error(f"Failed to open camera: {self.source_id}")
        else:
            logger.info("Camera connected.")

    def is_connected(self) -> bool:
        return self.cap is not None and self.cap.isOpened()

    def get_frames(self):

        while True:
            if not self.is_connected():
                logger.warning("Camera disconnected. Retrying in 5s...")
                time.sleep(5)
                self._connect()
                continue
            ret, frame = self.cap.read()
            if not ret:
                logger.warning("Frame read failed. Reconnecting...")
                self.cap.release()
                time.sleep(5)
                self._connect()
                continue
            yield frame

    def release(self):
        if self.cap:
            self.cap.release()
            logger.info("Camera released.")
