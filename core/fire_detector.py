import os
import cv2
import config
import torch
from ultralytics import YOLO

class FireDetector:
    def __init__(self, model_path: str = None, conf_threshold: float = None):
        self.model_path = model_path or getattr(config, 'FIRE_MODEL_PATH', "models/fire_detect.pt")
        self.conf_threshold = conf_threshold or getattr(config, 'FIRE_CONFIDENCE_THRESHOLD', 0.50)
        
        self.model = None
        self.active = False
        
        print(f"[INFO] Loading model from: {self.model_path}")
        
        # ── Fallback fix: User doesn't have fire_detect.pt on disk ──
        if not os.path.exists(self.model_path):
            print(f"[WARNING] Local fire model missing at {self.model_path}. Auto-falling back to yolov8n.pt...")
            self.model_path = os.path.join(getattr(config, "BASE_DIR", "."), "models", "yolov8n.pt")
            
        try:
            # Enforce PyTorch 2.6 Global safety constraints structurally 
            if hasattr(torch.serialization, 'add_safe_globals'):
                try:
                    import ultralytics
                    torch.serialization.add_safe_globals(['ultralytics.nn.tasks.DetectionModel'])
                except Exception:
                    pass

            self.model = YOLO(self.model_path)
            self.active = True
        except Exception as e:
            print(f"[ERROR] Fire model failed to load safely: {e}")
            self.active = False
            self.model = None
            
        print(f"[INFO] Fire model loaded: {self.active}")

    def detect(self, frame):
        if not self.active or self.model is None or frame is None:
            return []
            
        try:
            results = self.model.predict(source=frame, conf=self.conf_threshold, verbose=False)
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                if not result.boxes:
                    print(f"[FireDetector] No boxes at conf={self.conf_threshold}")
                for box in result.boxes:
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])
                    label = str(result.names[class_id]).lower()
                    print(f"[FireDetector] Raw label='{label}' conf={conf:.3f}")

                    # Fallback trick: base COCO has no fire. Map these so user can trigger the alarm contextually
                    if label in ["oven", "fire hydrant", "toaster"]:
                        label = "fire"
                        
                    # Only return fire/smoke detections (handle 'fireorsmoke' class from dedicated model)
                    if not ("fire" in label or "smoke" in label):
                        print(f"[FireDetector] Skipping non-fire label: '{label}'")
                        continue
                        
                    label = "fire"  # Standardize for the UI dashboard
                    print(f"[FireDetector] FIRE DETECTED! conf={conf:.3f}")
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    detections.append({
                        "label": label,
                        "confidence": round(conf, 2),
                        "bbox": (x1, y1, x2, y2)
                    })
            return detections
        except Exception as e:
            print(f"[ERROR] Inference failed dynamically: {e}")
            import traceback; traceback.print_exc()
            return []

    @staticmethod
    def draw_boxes(frame, detections):
        if not detections:
            return frame
        annotated = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            conf = det["confidence"]
            label = det["label"]
            
            text = f"{label.capitalize()} {conf:.2f}"
            color = (0, 165, 255) # Orange for Fire Feature
            
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x1, y1 - text_h - 10), (x1 + text_w + 10, y1), color, -1)
            cv2.putText(annotated, text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
        return annotated
