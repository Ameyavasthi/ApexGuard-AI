"""
core/alert_system.py — Real-time Alert Mechanism
"""
import time
import threading
import logging
import pygame
import config

logger = logging.getLogger(__name__)

class AlertSystem:
    def __init__(self):
        # Config-driven cooldown to prevent spam
        self.cooldown_seconds = getattr(config, 'ALERT_COOLDOWN_SECONDS', 10)
        self.siren_path = getattr(config, 'SIREN_SOUND_PATH', 'sounds/siren.mp3')
        
        self._last_alert_time = {}
        self._lock = threading.Lock()
        
        # Initialize pygame explicitly for safe non-blocking audio play
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(self.siren_path)
            self.audio_ready = True
            logger.info("Alert System (Siren) initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize siren audio: {e}")
            self.audio_ready = False

    def trigger_alert(self, label: str) -> bool:
        """
        Triggers a siren if the cooldown for this specific detection label has elapsed.
        
        Returns:
            bool: True if alert was triggered, False if ignored due to cooldown.
        """
        current_time = time.time()
        
        with self._lock:
            last_time = self._last_alert_time.get(label, 0)
            if current_time - last_time < self.cooldown_seconds:
                # Still on cooldown
                return False
                
            # Update cooldown timestamp
            self._last_alert_time[label] = current_time

        logger.warning(f"🚨 DANGER! {label.upper()} DETECTED! Triggering Siren!")
        
        # Play audio asynchronously (non-blocking)
        if self.audio_ready:
            # Leveraging thread prevents any slight IO freezing during .play()
            threading.Thread(target=self._play_sound, daemon=True).start()
            
        return True

    def _play_sound(self):
        try:
            # Loops=0 ensures it plays exactly once per trigger
            pygame.mixer.music.play(loops=0)
        except Exception as e:
            logger.error(f"Error attempting to play siren: {e}")
