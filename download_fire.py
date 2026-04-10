from huggingface_hub import hf_hub_download
import shutil
import os

print("Downloading dedicated fire detection model (YOLOv8)...")
try:
    path = hf_hub_download(repo_id="keremberke/yolov8s-fire-detection", filename="best.pt")
    # Move it from HF cache to our models directory
    dest = os.path.join("models", "fire_detect.pt")
    shutil.copy(path, dest)
    print(f"Success! Fire model saved to {dest}")
except Exception as e:
    print(f"Failed to download: {e}")
