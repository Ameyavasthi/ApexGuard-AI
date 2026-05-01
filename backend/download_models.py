import os, urllib.request

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def download(url, dest, label):
    if os.path.exists(dest):
        print(f"  ✓ Already exists: {label}"); return
    print(f"  ↓ Downloading {label}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print(f"  ✓ Saved → {dest}")
    except Exception as e:
        print(f"  ✗ Failed: {e}\n    Manually download from:\n    {url}\n    Save as: {dest}")

print("\n=== ApexGuard-AI Model Downloader ===\n")

download(
    url="https://github.com/spacewalk01/yolov9-fire-detection/releases/download/v1.0/yolov9-c-fire.pt",
    dest=os.path.join(MODELS_DIR, "fire_detect.pt"),
    label="Fire/Smoke Detection Model"
)

print()

animal_path = os.path.join(MODELS_DIR, "animal_detect.pt")
if os.path.exists(animal_path):
    print("  ✓ Animal model found!")
else:
    print("  → models/animal_detect.pt not found. Follow steps above.")

print("\n=== Done ===")
print("Run: uvicorn api.main:app --host 0.0.0.0 --port 8000\n")
