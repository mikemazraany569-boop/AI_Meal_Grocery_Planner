
from ultralytics import YOLO
from pathlib import Path


class IngredientDetector:

    def __init__(self, model_path="yolo11n.pt"):
        self.model = YOLO(model_path)

    def detect(self, image_path, confidence=0.25):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        results = self.model.predict(
            source=str(image_path),
            conf=confidence,
            save=True,
            show=False,
            device="cpu"
        )

        detections = []

        for result in results:
            for box in result.boxes:

                class_id = int(box.cls[0])
                label = self.model.names[class_id]
                score = float(box.conf[0])

                x1, y1, x2, y2 = (
                    box.xyxy[0].tolist()
                )

                detections.append({
                    "label": label,
                    "confidence": round(score, 4),
                    "box": [
                        round(x1, 2),
                        round(y1, 2),
                        round(x2, 2),
                        round(y2, 2)
                    ]
                })

        return detections
