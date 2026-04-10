import os
import cv2
import logging
import warnings
import torch
from ultralytics import YOLO
import config

logger = logging.getLogger(__name__)

class AnimalDetector:
    def __init__(self, model_path: str = None, conf_threshold: float = None):
        self.model_path = model_path or getattr(config, 'ANIMAL_MODEL_PATH', "models/animal_detect.pt")
        self.conf_threshold = conf_threshold or getattr(config, 'ANIMAL_CONFIDENCE_THRESHOLD', 0.5)
        self.dangerous_animals = getattr(config, 'DANGEROUS_ANIMALS', {"tiger", "lion", "bear", "leopard", "snake"})
        
        self.model = None

        print(f"[INFO] Loading model from: {self.model_path}")
        
        if not os.path.exists(self.model_path):
            print(f"[ERROR] Model not found at {self.model_path}")
            return

        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                
                # CRITICAL FIX (PyTorch 2.6 bug) - Allowing execution natively
                if hasattr(torch.serialization, 'add_safe_globals'):
                    try:
                        import ultralytics
                        # Pass exactly the string pattern PyTorch 2.6 requires + the class itself
                        torch.serialization.add_safe_globals([
                            'ultralytics.nn.tasks.DetectionModel', 
                            ultralytics.nn.tasks.DetectionModel
                        ])
                    except Exception as e:
                        logger.warning(f"Failed to add safe globals: {e}")
                
                self.model = YOLO(self.model_path)
                print("[INFO] Animal model loaded successfully")
                
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            self.model = None

    def detect(self, frame, log_non_dangerous: bool = False):
        # Work strictly ONLY if model successfully loaded
        if self.model is None or frame is None:
            return [], frame
            
        try:
            results = self.model.predict(source=frame, conf=self.conf_threshold, verbose=False)
            dangerous_detections = []
            annotated_frame = frame.copy()
            
            if results and len(results) > 0:
                result = results[0]
                for box in result.boxes:
                    conf = float(box.conf[0])
                    class_id = int(box.cls[0])
                    label = str(result.names[class_id]).lower()
                    
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    
                    if label in self.dangerous_animals:
                         dangerous_detections.append({
                             "label": label,
                             "confidence": round(conf, 2),
                             "bbox": (x1, y1, x2, y2)
                         })
                         self._draw_box(annotated_frame, label, conf, x1, y1, x2, y2, color=(0, 0, 255))
                         
                    elif log_non_dangerous:
                         self._draw_box(annotated_frame, f"Safe: {label}", conf, x1, y1, x2, y2, color=(0, 255, 0))
                         
            return dangerous_detections, annotated_frame
            
        except Exception as e:
            print(f"[ERROR] Inference failed safely: {e}")
            return [], frame

    def _draw_box(self, frame, label, conf, x1, y1, x2, y2, color):
        text = f"{label.capitalize()} {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w + 10, y1), color, -1)
        cv2.putText(frame, text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
    @staticmethod
    def draw_boxes(frame, detections: list):
        """Draw pre-computed detection boxes on a frame (used by optimised stream pipeline)."""
        if not detections:
            return frame
        annotated = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["label"]
            conf  = det["confidence"]
            color = (0, 0, 255)   # Red for dangerous animals
            text  = f"{label.capitalize()} {conf:.2f}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
            cv2.putText(annotated, text, (x1 + 5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return annotated
