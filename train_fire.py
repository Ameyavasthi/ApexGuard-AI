"""
Dedicated Fire & Smoke Model Training Pipeline
Follows the optimized fixes for maximum accuracy.
"""

from ultralytics import YOLO

def main():
    print("[INFO] Initializing new YOLOv8s Fire & Smoke Model Training...")

    # Fix 5 — Use a larger backbone (started with yolov8s base)
    model = YOLO("yolov8s.pt")  

    # Fix 1 & Fix 4 — Train for many more epochs (100) using the separated dataset yaml
    # This directly uses the fire_dataset.yaml we just generated
    print("[INFO] Starting training phase (100 Epochs / Batch 16)...")
    model.train(
        data="fire_dataset.yaml", 
        epochs=100, 
        imgsz=640, 
        batch=16,
        project="runs",     # Custom directory for saved weights
        name="fire_smoke_v2"
    )
    print("\n[SUCCESS] Training complete. The new best.pt will be saved in runs/fire_smoke_v2/weights/")

if __name__ == "__main__":
    main()
