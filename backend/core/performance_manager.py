import psutil
import time
import logging
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)

class PerformanceMode(Enum):
    HIGH = "high"      # Full detection every frame
    BALANCED = "balanced"  # Skip frames, sequential models
    LOW = "low"        # Minimal processing

@dataclass
class PerformanceConfig:
    mode: PerformanceMode
    infer_every_n: int
    infer_width: int
    stream_quality: int
    max_active_models: int
    cpu_threshold: float

PERFORMANCE_PROFILES = {
    PerformanceMode.HIGH: PerformanceConfig(
        mode=PerformanceMode.HIGH,
        infer_every_n=1,
        infer_width=640,
        stream_quality=85,
        max_active_models=3,  # Allow parallel models
        cpu_threshold=80.0
    ),
    PerformanceMode.BALANCED: PerformanceConfig(
        mode=PerformanceMode.BALANCED,
        infer_every_n=3,
        infer_width=416,
        stream_quality=65,
        max_active_models=1,  # Sequential models
        cpu_threshold=60.0
    ),
    PerformanceMode.LOW: PerformanceConfig(
        mode=PerformanceMode.LOW,
        infer_every_n=5,
        infer_width=320,
        stream_quality=50,
        max_active_models=1,
        cpu_threshold=40.0
    )
}

class PerformanceManager:
    def __init__(self, initial_mode: PerformanceMode = PerformanceMode.BALANCED):
        self.current_mode = initial_mode
        self.config = PERFORMANCE_PROFILES[initial_mode]
        self.last_cpu_check = 0
        self.cpu_check_interval = 5.0  # Check CPU every 5 seconds

    def get_config(self) -> PerformanceConfig:

        return self.config

    def set_mode(self, mode: PerformanceMode):

        self.current_mode = mode
        self.config = PERFORMANCE_PROFILES[mode]
        logger.info(f"Performance mode set to: {mode.value}")

    def auto_adjust(self) -> bool:

        current_time = time.time()
        if current_time - self.last_cpu_check < self.cpu_check_interval:
            return False

        self.last_cpu_check = current_time
        cpu_percent = psutil.cpu_percent(interval=1.0)

        if cpu_percent > 80 and self.current_mode != PerformanceMode.LOW:
            self.set_mode(PerformanceMode.LOW)
            logger.warning(f"High CPU ({cpu_percent:.1f}%) - Switching to LOW power mode")
            return True
        elif cpu_percent > 60 and self.current_mode == PerformanceMode.HIGH:
            self.set_mode(PerformanceMode.BALANCED)
            logger.warning(f"Moderate CPU ({cpu_percent:.1f}%) - Switching to BALANCED mode")
            return True
        elif cpu_percent < 40 and self.current_mode == PerformanceMode.LOW:
            self.set_mode(PerformanceMode.BALANCED)
            logger.info(f"Low CPU ({cpu_percent:.1f}%) - Switching to BALANCED mode")
            return True
        elif cpu_percent < 20 and self.current_mode != PerformanceMode.HIGH:
            self.set_mode(PerformanceMode.HIGH)
            logger.info(f"Very low CPU ({cpu_percent:.1f}%) - Switching to HIGH performance mode")
            return True

        return False

    def get_stats(self) -> dict:

        return {
            "mode": self.current_mode.value,
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "config": {
                "infer_every_n": self.config.infer_every_n,
                "infer_width": self.config.infer_width,
                "stream_quality": self.config.stream_quality,
                "max_active_models": self.config.max_active_models
            }
        }
