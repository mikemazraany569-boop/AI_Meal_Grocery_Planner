
from pathlib import Path

from huggingface_hub import hf_hub_download
from ultralytics import YOLO


class IngredientDetector:
    """Detect fruits and vegetables using a specialized YOLOv8n model."""

    MODEL_REPO = "Aniket2003333333/fruit-veg-yolov8n-detector"
    MODEL_FILENAME = "best.pt"

    def __init__(self, model_path=None):
        """
        Load the fruit and vegetable detector.

        Args:
            model_path: Optional local path to custom YOLO weights.
        """

        if model_path is None:
            model_path = hf_hub_download(
                repo_id=self.MODEL_REPO,
                filename=self.MODEL_FILENAME,
            )

        self.model_path = str(model_path)
        self.model = YOLO(self.model_path)

    @staticmethod
    def _normalize_label(label):
        """Normalize model labels for ingredient mapping."""

        return (
            str(label)
            .replace("_", " ")
            .strip()
            .lower()
        )

    def detect(self, image_path, confidence=0.25):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0 < confidence <= 1
        ):
            raise ValueError(
                "Confidence must be greater than 0 "
                "and less than or equal to 1."
            )

        results = self.model.predict(
            source=str(image_path),
            conf=confidence,
            imgsz=640,
            save=False,
            show=False,
            device="cpu",
            verbose=False,
        )

        detections = []

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])

                original_label = self.model.names[class_id]

                label = self._normalize_label(
                    original_label
                )

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
                        round(y2, 2),
                    ],
                })

        return detections
