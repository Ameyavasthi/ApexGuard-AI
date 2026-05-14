import os
import cv2
import logging
import warnings
import torch
from ultralytics import YOLO
import config

logger = logging.getLogger(__name__)


def _load_yolo_model(path: str, label: str = ""):
    """Safely load a YOLO model with PyTorch 2.6+ compatibility."""
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # PyTorch 2.6+ defaults weights_only=True which breaks custom YOLO .pt files.
            _original_torch_load = torch.load
            def _patched_load(*args, **kwargs):
                kwargs.setdefault('weights_only', False)
                return _original_torch_load(*args, **kwargs)
            torch.load = _patched_load

            model = YOLO(path)

            torch.load = _original_torch_load
            print(f"[INFO] {label or 'Model'} loaded successfully from: {path}")
            return model

    except Exception as e:
        print(f"[ERROR] Failed to load {label or 'model'} from {path}: {e}")
        return None


class AnimalDetector:
    """
    Dual-model animal detector:
      - Primary:   animal_detect.pt  (custom — Lion, Tiger, Gorilla, Elephant, Giraffe, Zebra)
      - Secondary:  yolov8n.pt       (COCO — Bear, Dog/Wolf, Cat, Horse, Bird, etc.)
    Both models run on each frame and results are merged with IoU de-duplication.
    """

    # COCO labels that should be mapped to more specific threat names
    COCO_LABEL_MAP = {
        "dog": "wolf",  # COCO doesn't have 'wolf'; large canines detected as 'dog'
    }

    def __init__(self, model_path: str = None, conf_threshold: float = None):
        self.model_path = model_path or getattr(config, 'ANIMAL_MODEL_PATH', "models/animal_detect.pt")
        self.conf_threshold = conf_threshold or getattr(config, 'ANIMAL_CONFIDENCE_THRESHOLD', 0.5)
        self.dangerous_animals = getattr(config, 'DANGEROUS_ANIMALS', {
            "tiger", "lion", "bear", "leopard", "snake", "wolf", "gorilla"
        })

        # ── Primary model (custom wildlife) ──
        self.model = None
        if os.path.exists(self.model_path):
            self.model = _load_yolo_model(self.model_path, label="Animal (wildlife) model")
        else:
            print(f"[WARNING] Custom animal model not found at {self.model_path}")

        # ── Secondary model (COCO — bear, dog, cat, etc.) ──
        self.coco_model = None
        coco_path = os.path.join(getattr(config, 'ROOT_DIR', '.'), "models", "yolov8n.pt")
        if not os.path.exists(coco_path):
            coco_path = os.path.join(getattr(config, 'BASE_DIR', '.'), "yolov8n.pt")
        if os.path.exists(coco_path):
            self.coco_model = _load_yolo_model(coco_path, label="Animal (COCO) model")
        else:
            print(f"[WARNING] COCO model not found — bear/wolf detection unavailable")

        # COCO animal class IDs we care about (subset of all 80 COCO classes)
        self.coco_animal_ids = {14, 15, 16, 17, 18, 19, 20, 21, 22, 23}
        # 14:bird, 15:cat, 16:dog, 17:horse, 18:sheep, 19:cow,
        # 20:elephant, 21:bear, 22:zebra, 23:giraffe

    def detect(self, frame, log_non_dangerous: bool = False):

        if frame is None:
            return [], frame

        all_detections = []
        annotated_frame = frame.copy()

        # ── Run primary (custom wildlife) model ──
        if self.model is not None:
            try:
                results = self.model.predict(source=frame, conf=self.conf_threshold, verbose=False)
                if results and len(results) > 0:
                    result = results[0]
                    for box in result.boxes:
                        conf = float(box.conf[0])
                        class_id = int(box.cls[0])
                        label = str(result.names[class_id]).lower()
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        if label in self.dangerous_animals:
                            all_detections.append({
                                "label": label,
                                "confidence": round(conf, 2),
                                "bbox": (x1, y1, x2, y2),
                                "source": "wildlife"
                            })
            except Exception as e:
                logger.error(f"Wildlife model inference error: {e}")

        # ── Run secondary (COCO) model ──
        if self.coco_model is not None:
            try:
                results = self.coco_model.predict(source=frame, conf=self.conf_threshold, verbose=False)
                if results and len(results) > 0:
                    result = results[0]
                    for box in result.boxes:
                        conf = float(box.conf[0])
                        class_id = int(box.cls[0])

                        # Only process animal classes from COCO
                        if class_id not in self.coco_animal_ids:
                            continue

                        raw_label = str(result.names[class_id]).lower()
                        # Map COCO labels (e.g. "dog" → "wolf")
                        label = self.COCO_LABEL_MAP.get(raw_label, raw_label)
                        x1, y1, x2, y2 = map(int, box.xyxy[0])

                        if label in self.dangerous_animals:
                            all_detections.append({
                                "label": label,
                                "confidence": round(conf, 2),
                                "bbox": (x1, y1, x2, y2),
                                "source": "coco"
                            })
            except Exception as e:
                logger.error(f"COCO model inference error: {e}")

        # ── De-duplicate overlapping detections from both models ──
        final_detections = self._deduplicate(all_detections)

        # ── Draw bounding boxes ──
        for det in final_detections:
            x1, y1, x2, y2 = det["bbox"]
            self._draw_box(annotated_frame, det["label"], det["confidence"],
                           x1, y1, x2, y2, color=(0, 0, 255))

        # Remove internal 'source' key before returning
        for det in final_detections:
            det.pop("source", None)

        return final_detections, annotated_frame

    def _deduplicate(self, detections, iou_threshold=0.5):
        """Remove duplicate detections from overlapping models using IoU."""
        if len(detections) <= 1:
            return detections

        # Sort by confidence (highest first)
        detections = sorted(detections, key=lambda d: d["confidence"], reverse=True)
        keep = []

        for det in detections:
            is_dup = False
            for kept in keep:
                if self._iou(det["bbox"], kept["bbox"]) > iou_threshold:
                    is_dup = True
                    break
            if not is_dup:
                keep.append(det)
        return keep

    @staticmethod
    def _iou(box1, box2):
        """Calculate Intersection over Union between two bounding boxes."""
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - inter
        return inter / union if union > 0 else 0

    def _draw_box(self, frame, label, conf, x1, y1, x2, y2, color):
        text = f"{label.capitalize()} {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (text_w, text_h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1 - text_h - 10), (x1 + text_w + 10, y1), color, -1)
        cv2.putText(frame, text, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    @staticmethod
    def draw_boxes(frame, detections: list):

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
