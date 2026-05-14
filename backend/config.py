import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)
load_dotenv(os.path.join(BASE_DIR, ".env"))

def _float(key: str, default: float) -> float:
    return float(os.getenv(key, default))

def _int(key: str, default: int) -> int:
    return int(os.getenv(key, default))

def _str(key: str, default: str) -> str:
    return os.getenv(key, default)

WEBCAM_SOURCE    = _int("WEBCAM_SOURCE", 0)
IP_CAMERA_SOURCE = _str("IP_CAMERA_SOURCE", "http://192.168.1.100:8080/video")
ACTIVE_CAMERA    = _str("ACTIVE_CAMERA", "webcam")   # "webcam" | "ip_camera"

ANIMAL_MODEL_PATH  = os.path.join(ROOT_DIR, "models", "animal_detect.pt")
FIRE_MODEL_PATH    = os.path.join(ROOT_DIR, "models", "fire_detect.pt")
WEAPON_MODEL_PATH  = os.path.join(ROOT_DIR, "models", "weapon_detect.pt")

ANIMAL_CONFIDENCE_THRESHOLD  = _float("ANIMAL_CONFIDENCE_THRESHOLD", 0.50)
FIRE_CONFIDENCE_THRESHOLD    = _float("FIRE_CONFIDENCE_THRESHOLD",   0.50)
WEAPON_CONFIDENCE_THRESHOLD  = _float("WEAPON_CONFIDENCE_THRESHOLD", 0.40)

DANGEROUS_ANIMALS = {"snake", "tiger", "lion", "leopard", "bear", "wolf", "gorilla"}

HARMFUL_WEAPON_LABELS = {
    "gun", "handgun", "pistol", "rifle", "revolver", "weapon",
    "knife", "scissors",
}

ALERT_COOLDOWN_SECONDS = _int("ALERT_COOLDOWN_SECONDS", 30)

SIREN_SOUND_PATH = os.path.join(BASE_DIR, "sounds", "siren.mp3")

SNAPSHOTS_DIR  = os.path.join(ROOT_DIR, "recordings_snapshots", "snapshots")
RECORDINGS_DIR = os.path.join(ROOT_DIR, "recordings_snapshots", "recordings")
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)
os.makedirs(RECORDINGS_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(BASE_DIR, 'surveillance.db')}"

FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")

CLIP_DURATION_SECONDS   = _int("CLIP_DURATION_SECONDS",    8)
CAMERA_FPS              = _int("CAMERA_FPS",               20)
PRE_EVENT_BUFFER_FRAMES = _int("PRE_EVENT_BUFFER_FRAMES",  40)

HOST = _str("HOST", "0.0.0.0")
PORT = _int("PORT", 8005)
