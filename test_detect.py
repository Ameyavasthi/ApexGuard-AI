"""
test_detect.py - Validation script for Animal, Fire, and Weapon Detectors
"""
import cv2
import sys
from core.animal_detector import AnimalDetector
from core.fire_detector import FireDetector
from core.weapon_detector import WeaponDetector

def main():
    print("="*50)
    print("ApexGuard-AI: Detector Test Script")
    print("="*50)
    
    # 1. Initialize detectors
    print("[INFO] Initializing Detectors...")
    
    animal_detector = AnimalDetector(conf_threshold=0.5)
    fire_detector = FireDetector(conf_threshold=0.1)
    weapon_detector = WeaponDetector(conf_threshold=0.4)
    
    # Check if models loaded
    models_ready = any([
        animal_detector.model is not None,
        fire_detector.model is not None,
        weapon_detector.model is not None
    ])
    
    if not models_ready:
        print("[ERROR] No models found. Please download models first.")
        sys.exit(1)
        
    # 2. Open webcam
    print("[INFO] Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("[ERROR] Could not access the webcam.")
        sys.exit(1)
        
    print("[INFO] Webcam opened successfully.")
    print("[INFO] Press 'q' in the video window to quit.")
    print("-" * 50)
    
    # 3. Process video frames
    while True:
        ret, frame = cap.read()
        
        if not ret:
            print("[ERROR] Failed to grab frame from camera. Exiting...")
            break
            
        annotated_frame = frame.copy()
        
        # 4. Perform inferences
        # Animal Detection
        if animal_detector.model:
            animal_dets, annotated_frame = animal_detector.detect(annotated_frame)
            if animal_dets:
                print(f"[Animal] {len(animal_dets)} Detected")
                
        # Fire Detection
        if fire_detector.model:
            fire_dets = fire_detector.detect(frame)
            if fire_dets:
                print(f"[Fire] {len(fire_dets)} Detected")
            annotated_frame = FireDetector.draw_boxes(annotated_frame, fire_dets)
            
        # Weapon Detection
        if weapon_detector.model:
            weapon_dets, annotated_frame = weapon_detector.detect(annotated_frame)
            if weapon_dets:
                print(f"[Weapon] {len(weapon_dets)} Detected")
                
        # 6. Display annotated video
        cv2.imshow("ApexGuard-AI - Detection Test", annotated_frame)
        
        # 7. Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[INFO] 'q' pressed. Exiting...")
            break
            
    # Clean up resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
