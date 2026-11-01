"""Ripeness classification with the trained YOLOv8-cls model (models/best.pt).

Class names look like 'mango_ripe' / 'banana_overripe' (folder names from training).
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "best.pt"
CONF_THRESHOLD = 0.50       # below this we ask for another photo (SRS alternative flow)

_model = None


class RipenessModelMissing(RuntimeError):
    pass


def split_label(name: str) -> tuple[str, str]:
    fruit, _, ripeness = name.partition("_")
    return fruit.lower(), ripeness.lower()


def _load():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise RipenessModelMissing(
                "models/best.pt nahi mila. Pehle Colab par training/train_ripeness.py chalao.")
        from ultralytics import YOLO          # imported lazily: app opens fast
        _model = YOLO(str(MODEL_PATH))
    return _model


def predict_ripeness(image: Image.Image, conf_threshold: float = CONF_THRESHOLD) -> dict:
    model = _load()
    res = model.predict(image.convert("RGB"), imgsz=224, verbose=False)[0]
    probs = res.probs
    names = res.names
    top = probs.top1
    fruit, ripeness = split_label(names[top])
    conf = float(probs.top1conf)
    order = probs.data.argsort(descending=True)[:3].tolist()
    return {
        "fruit": fruit,
        "ripeness": ripeness,
        "confidence": conf,
        "confident": conf >= conf_threshold,
        "top3": [(names[i], float(probs.data[i])) for i in order],
    }
