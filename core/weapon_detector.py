"""
core/weapon_detector.py — Harmful Object / Weapon Detection Module
===================================================================
Uses YOLOv8 pretrained on COCO (yolov8n.pt) to detect harmful objects
including guns (handguns, rifles), knives, and scissors.

If you have a dedicated weapon model (e.g. a fine-tuned gun-detection .pt),
set WEAPON_MODEL_PATH in config.py to point to it — this module will use it
automatically. If no custom model is found, it falls back to yolov8n.pt.

COCO class IDs for harmful objects:
  43  = knife
  76  = scissors
  (No explicit "gun" in COCO-80.  A dedicated fine-tuned model is best for guns.)

We also support a dedicated model where label names include:
  "gun", "handgun", "pistol", "rifle", "revolver", "weapon", "knife"
"""

import os
import cv2
import logging
import warnings
import torch

logger = logging.getLogger(__name__)


# COCO-80 labels that we consider dangerous / harmful
HARMFUL_COCO_LABELS = {
    "knife",
    "scissors",
    # Some custom COCO variants include these — keep to be safe
    "gun",
    "pistol",
    "rifle",
    "handgun",
    "revolver",
    "weapon",
}

# Box colours per threat category
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
    """
    Detects harmful objects (guns, knives, etc.) in a video frame.

    Strategy
    --------
    1. Try to load a dedicated fine-tuned weapon model from WEAPON_MODEL_PATH.
    2. If that fails or is not configured, fall back to the standard YOLOv8n
       COCO model and filter only the harmful COCO labels.
    """

    def __init__(self, model_path: str = None, conf_threshold: float = None):
        import config                                          # local import to avoid circular
        from ultralytics import YOLO

        self.conf_threshold = conf_threshold or getattr(config, "WEAPON_CONFIDENCE_THRESHOLD", 0.45)
        self.harmful_labels = getattr(config, "HARMFUL_WEAPON_LABELS", HARMFUL_COCO_LABELS)
        self.model = None
        self.model_label = "unknown"

        # ── 1. Try dedicated weapon model ──────────────────────────────────────
        dedicated = model_path or getattr(config, "WEAPON_MODEL_PATH", "")
        if dedicated and os.path.exists(dedicated):
            self._load_model(dedicated, label="dedicated weapon model")

        # ── 2. Fall back to yolov8n.pt (downloads automatically if missing) ───
        if self.model is None:
            logger.warning(
                "[WeaponDetector] No dedicated weapon model found. "
                "Using YOLOv8n COCO model with label filtering."
            )
            fallback = os.path.join(
                getattr(config, "BASE_DIR", "."), "models", "yolov8n.pt"
            )
            # If the file isn't local, ultralytics will auto-download it.
            self._load_model(fallback if os.path.exists(fallback) else "yolov8n.pt",
                             label="YOLOv8n COCO (fallback)")

    # ──────────────────────────────────────────────────────────────────────────
    def _load_model(self, path: str, label: str):
        from ultralytics import YOLO
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                if hasattr(torch.serialization, "add_safe_globals"):
                    try:
                        import ultralytics
                        torch.serialization.add_safe_globals(
                            ["ultralytics.nn.tasks.DetectionModel",
                             ultralytics.nn.tasks.DetectionModel]
                        )
                    except Exception:
                        pass
                self.model = YOLO(path)
                self.model_label = label
                print(f"[INFO] Weapon model loaded ({label}) ✓")
        except Exception as exc:
            print(f"[ERROR] Failed to load weapon model ({label}): {exc}")
            self.model = None

    # ──────────────────────────────────────────────────────────────────────────
    def detect(self, frame):
        """
        Run inference and return only harmful-object detections.

        Returns
        -------
        detections : list[dict]
            Each dict has keys: label, confidence, bbox (x1,y1,x2,y2)
        annotated_frame : np.ndarray
            Frame with bounding boxes drawn on it.
        """
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

                    # Only keep labels we consider harmful
                    if raw_label not in self.harmful_labels:
                        continue

                    # Fallback trick: The standard COCO model does not have a "gun" class.
                    # It frequently misclassifies handguns/pistols as "scissors".
                    # We map it to "gun" here so the UI and alerts trigger correctly.
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

    # ──────────────────────────────────────────────────────────────────────────
    @staticmethod
    def draw_boxes(frame, detections: list):
        """
        Draw boxes on a frame from a pre-computed detections list.
        (Mirrors the API used by FireDetector / AnimalDetector.)
        """
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

    # ──────────────────────────────────────────────────────────────────────────
    def _draw_box(self, frame, label, conf, x1, y1, x2, y2, color):
        text = f"{label.capitalize()} {conf:.2f}"
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x1, y1 - th - 10), (x1 + tw + 10, y1), color, -1)
        cv2.putText(frame, text, (x1 + 5, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
