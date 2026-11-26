
from pathlib import Path

from huggingface_hub import hf_hub_download
from ultralytics import YOLO


# Download or reuse the cached model.
weights_path = hf_hub_download(
    repo_id="Aniket2003333333/fruit-veg-yolov8n-detector",
    filename="best.pt",
)

model = YOLO(weights_path)

image_dir = Path("data/images")

image_names = [
    "20261124_173345.jpg",
    "20261124_173400.jpg",
    "20261124_173403.jpg",
    "20261124_173510.jpg",
    "20261125_140129.jpg",
]

print("=" * 65)
print("FRUIT AND VEGETABLE MODEL TEST")
print("=" * 65)

print("\nSupported classes:", len(model.names))

for image_name in image_names:
    image_path = image_dir / image_name

    if not image_path.exists():
        print(f"\nMissing image: {image_path}")
        continue

    results = model.predict(
        source=str(image_path),
        conf=0.25,
        imgsz=640,
        device="cpu",
        save=False,
        verbose=False,
    )

    print(f"\nImage: {image_name}")

    detections = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            label = model.names[class_id]
            confidence = float(box.conf[0])

            detections.append((label, confidence))

    if not detections:
        print("  No ingredients detected.")
    else:
        for label, confidence in detections:
            print(f"  {label}: {confidence:.3f}")

print("\nTest completed.")
