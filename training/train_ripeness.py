"""Train the YOLOv8 ripeness classifier (run on Google Colab with a T4 GPU).

    pip install ultralytics
    python training/train_ripeness.py --data data --epochs 30
Output: models/best.pt  (+ confusion matrix and result plots in runs/classify/ripeness/)
"""
import argparse, shutil
from pathlib import Path
from ultralytics import YOLO

ap = argparse.ArgumentParser()
ap.add_argument("--data", default="data")
ap.add_argument("--epochs", type=int, default=30)
ap.add_argument("--imgsz", type=int, default=224)
a = ap.parse_args()

model = YOLO("yolov8n-cls.pt")   # small pretrained model (transfer learning)
model.train(data=a.data, epochs=a.epochs, imgsz=a.imgsz, project="runs/classify",
            name="ripeness", exist_ok=True)

best = Path("runs/classify/ripeness/weights/best.pt")
Path("models").mkdir(exist_ok=True)
shutil.copy(best, "models/best.pt")
metrics = YOLO("models/best.pt").val(data=a.data)
print("Top-1 accuracy:", metrics.top1, "| Top-5:", metrics.top5)
print("Saved models/best.pt. Class names:", YOLO("models/best.pt").names)
