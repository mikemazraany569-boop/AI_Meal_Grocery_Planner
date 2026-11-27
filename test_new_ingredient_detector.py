
from src.vision.ingredient_detector import IngredientDetector
from src.vision.detection_mapper import DetectionMapper

from pathlib import Path


detector = IngredientDetector()
mapper = DetectionMapper()

image_dir = Path("data/images")

images = [
    "20261124_173345.jpg",
    "20261124_173400.jpg",
    "20261124_173403.jpg",
    "20261124_173510.jpg",
    "20261125_140129.jpg",
]

for image_name in images:

    image_path = image_dir / image_name

    print("\n" + "=" * 60)
    print("IMAGE:", image_name)
    print("=" * 60)

    detections = detector.detect(
        image_path,
        confidence=0.25,
    )

    if not detections:
        print("No detections.")
        continue

    for detection in detections:

        mapped = mapper.map_detection(detection)

        print(
            f"Detected: {detection['label']} "
            f"| Confidence: {detection['confidence']}"
        )

        print("Mapped:", mapped)
