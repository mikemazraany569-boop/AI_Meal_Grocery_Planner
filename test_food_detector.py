
from ultralytics import YOLO
from pathlib import Path

MODEL_PATH = Path("models/vision/food_detector.onnx")

# Replace this with the path to your test photograph
IMAGE_PATH = Path("data/images/image.jpg")

model = YOLO(str(MODEL_PATH), task="detect")

print("MODEL:", MODEL_PATH.resolve())
print("MODEL TASK:", model.task)
print("MODEL CLASSES:", model.names)

results = model.predict(
    source=str(IMAGE_PATH),
    imgsz=640,
    conf=0.25,
    save=True,
    verbose=False
)

print("\nFOOD INGREDIENT DETECTIONS")
print("=" * 40)

for result in results:
    if result.boxes is None or len(result.boxes) == 0:
        print("No ingredients detected.")
        continue

    for box in result.boxes:
        class_id = int(box.cls.item())
        confidence = float(box.conf.item())
        name = model.names[class_id]

        print(f"{name:20s} Confidence: {confidence:.2%}")

print("\nDetection image saved by Ultralytics.")
