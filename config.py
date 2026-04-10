"""
config.py — Central Configuration
==================================
All runtime settings live here.  Values are loaded from the .env file
(or system environment variables) via python-dotenv, so you never need
to hard-code secrets into source code.

Precedence:  .env file  →  environment variable  →  default value
"""

import os
from dotenv import load_dotenv

# Load .env from the project root (same directory as this file)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# ── Helper ────────────────────────────────────────────────────────────────────
def _float(key: str, default: float) -> float:
    return float(os.getenv(key, default))

def _int(key: str, default: int) -> int:
    return int(os.getenv(key, default))

def _str(key: str, default: str) -> str:
    return os.getenv(key, default)

# ── Camera Sources ────────────────────────────────────────────────────────────
WEBCAM_SOURCE    = _int("WEBCAM_SOURCE", 0)
IP_CAMERA_SOURCE = _str("IP_CAMERA_SOURCE", "http://192.168.1.100:8080/video")
ACTIVE_CAMERA    = _str("ACTIVE_CAMERA", "webcam")   # "webcam" | "ip_camera"

# ── Model Paths ───────────────────────────────────────────────────────────────
ANIMAL_MODEL_PATH  = os.path.join(BASE_DIR, "models", "animal_detect.pt")
FIRE_MODEL_PATH    = os.path.join(BASE_DIR, "models", "fire_detect.pt")
WEAPON_MODEL_PATH  = os.path.join(BASE_DIR, "models", "weapon_detect.pt")

# ── Detection Thresholds ──────────────────────────────────────────────────────
ANIMAL_CONFIDENCE_THRESHOLD  = _float("ANIMAL_CONFIDENCE_THRESHOLD", 0.50)
FIRE_CONFIDENCE_THRESHOLD    = _float("FIRE_CONFIDENCE_THRESHOLD",   0.50)
WEAPON_CONFIDENCE_THRESHOLD  = _float("WEAPON_CONFIDENCE_THRESHOLD", 0.40)

# ── Dangerous Animals ─────────────────────────────────────────────────────────
DANGEROUS_ANIMALS = {"snake", "tiger", "lion", "leopard", "bear"}

# ── Harmful Weapon Labels ─────────────────────────────────────────────────────
HARMFUL_WEAPON_LABELS = {
    "gun", "handgun", "pistol", "rifle", "revolver", "weapon",
    "knife", "scissors",
}

# ── Alert Cooldown ────────────────────────────────────────────────────────────
ALERT_COOLDOWN_SECONDS = _int("ALERT_COOLDOWN_SECONDS", 30)

# ── Sound ─────────────────────────────────────────────────────────────────────
SIREN_SOUND_PATH = os.path.join(BASE_DIR, "sounds", "siren.mp3")

# ── Storage Directories ───────────────────────────────────────────────────────
SNAPSHOTS_DIR  = os.path.join(BASE_DIR, "snapshots")
RECORDINGS_DIR = os.path.join(BASE_DIR, "recordings")
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'surveillance.db')}"

# ── Video Recording ───────────────────────────────────────────────────────────
CLIP_DURATION_SECONDS   = _int("CLIP_DURATION_SECONDS",    8)
CAMERA_FPS              = _int("CAMERA_FPS",               20)
PRE_EVENT_BUFFER_FRAMES = _int("PRE_EVENT_BUFFER_FRAMES",  40)

# ── API ───────────────────────────────────────────────────────────────────────
HOST = _str("HOST", "0.0.0.0")
PORT = _int("PORT", 8005)
