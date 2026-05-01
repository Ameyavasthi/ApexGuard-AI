import time
import threading
import logging
import pygame
import config

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):

        self.cooldown_seconds = getattr(config, 'ALERT_COOLDOWN_SECONDS', 10)
        self.siren_path = getattr(config, 'SIREN_SOUND_PATH', 'sounds/siren.mp3')

        self._last_alert_time = {}
        self._lock = threading.Lock()

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(self.siren_path)
            self.audio_ready = True
            logger.info("Alert System (Siren) initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize siren audio: {e}")
            self.audio_ready = False

    def trigger_alert(self, label: str) -> bool:

        current_time = time.time()

        with self._lock:
            last_time = self._last_alert_time.get(label, 0)
            if current_time - last_time < self.cooldown_seconds:

                return False

            self._last_alert_time[label] = current_time

        logger.warning(f"🚨 DANGER! {label.upper()} DETECTED! Triggering Siren!")

        if self.audio_ready:

            threading.Thread(target=self._play_sound, daemon=True).start()

        return True

    def _play_sound(self):
        try:

            pygame.mixer.music.play(loops=0)
        except Exception as e:
            logger.error(f"Error attempting to play siren: {e}")
