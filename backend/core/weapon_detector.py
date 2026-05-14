import os
import cv2
import logging
import warnings
import torch

logger = logging.getLogger(__name__)

HARMFUL_COCO_LABELS = {
    "knife",
    "scissors",

    "gun",
    "pistol",
    "rifle",
    "handgun",
    "revolver",
    "weapon",
}

COLOUR_MAP = {
    "knife":    (0,  50, 255),   # vivid red
    "scissors": (0, 120, 255),   # orange-red
    "gun":      (0,   0, 255),   # pure red
    "pistol":   (0,   0, 255),
    "rifle":    (0,   0, 255),
    "handgun":  (0,   0, 255),
    "revolver": (0,   0, 255),
    "weapon":   (0,   0, 255),
    "_default": (0,  80, 220),   # fallback red-ish
}

class WeaponDetector:

    def __init__(self, model_path: str = None, conf_threshold: float = None):
        import config                                          # local import to avoid circular
        from ultralytics import YOLO

        self.conf_threshold = conf_threshold or getattr(config, "WEAPON_CONFIDENCE_THRESHOLD", 0.45)
        self.harmful_labels = getattr(config, "HARMFUL_WEAPON_LABELS", HARMFUL_COCO_LABELS)
        self.model = None
        self.model_label = "unknown"

        dedicated = model_path or getattr(config, "WEAPON_MODEL_PATH", "")
        if dedicated and os.path.exists(dedicated):
            self._load_model(dedicated, label="dedicated weapon model")

        if self.model is None:
            logger.warning(
                "[WeaponDetector] No dedicated weapon model found. "
                "Using YOLOv8n COCO model with label filtering."
            )
            fallback = os.path.join(
                getattr(config, "BASE_DIR", "."), "models", "yolov8n.pt"
            )

            self._load_model(fallback if os.path.exists(fallback) else "yolov8n.pt",
                             label="YOLOv8n COCO (fallback)")

    def _load_model(self, path: str, label: str):
        from ultralytics import YOLO
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")

                # PyTorch 2.6+ defaults weights_only=True which breaks custom YOLO .pt files.
                _original_torch_load = torch.load
                def _patched_load(*args, **kwargs):
                    kwargs.setdefault('weights_only', False)
                    return _original_torch_load(*args, **kwargs)
                torch.load = _patched_load

                self.model = YOLO(path)

                torch.load = _original_torch_load
                self.model_label = label
                print(f"[INFO] Weapon model loaded ({label}) ✓")
        except Exception as exc:
            print(f"[ERROR] Failed to load weapon model ({label}): {exc}")
            self.model = None

    def detect(self, frame):

        if self.model is None or frame is None:
            return [], frame

        try:
            results = self.model.predict(source=frame, conf=self.conf_threshold, verbose=False)
            detections = []
            annotated = frame.copy()

            if results and len(results) > 0:
                result = results[0]
                for box in result.boxes:
                    conf       = float(box.conf[0])
                    class_id   = int(box.cls[0])
                    raw_label  = str(result.names[class_id]).lower()

                    if raw_label not in self.harmful_labels:
                        continue

                    if raw_label == "scissors":
                        raw_label = "gun"

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    detections.append({
                        "label":      raw_label,
                        "confidence": round(conf, 2),
                        "bbox":       (x1, y1, x2, y2),
                    })
                    color = COLOUR_MAP.get(raw_label, COLOUR_MAP["_default"])
                    self._draw_box(annotated, raw_label, conf, x1, y1, x2, y2, color)

            return detections, annotated

        except Exception as exc:
            logger.error(f"[WeaponDetector] Inference error: {exc}")
            return [], frame

    @staticmethod
    def draw_boxes(frame, detections: list):

        if not detections:
            return frame
        annotated = frame.copy()
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            label = det["label"]
            conf  = det["confidence"]
            color = COLOUR_MAP.get(label, COLOUR_MAP["_default"])
            text  = f"{label.capitalize()} {conf:.2f}"
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
            (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(annotated, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
            cv2.putText(annotated, text, (x1 + 5, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        return annotated

    def _draw_box(self, frame, label, conf, x1, y1, x2, y2, color):
        text = f"{label.capitalize()} {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
        cv2.putText(frame, text, (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
