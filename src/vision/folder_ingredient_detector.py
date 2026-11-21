
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

from src.inventory.folder_processor import FolderProcessor
from src.vision.ingredient_detector import IngredientDetector


class FolderIngredientDetector:
    """Detect ingredients across multiple uploaded images."""

    def __init__(
        self,
        ingredient_detector=None,
        folder_processor=None,
    ):
        self.ingredient_detector = (
            ingredient_detector or IngredientDetector()
        )

        self.folder_processor = (
            folder_processor or FolderProcessor()
        )

    def process(self, uploaded_files, confidence=0.25):

        if (
            isinstance(confidence, bool)
            or not isinstance(confidence, (int, float))
            or not 0 < confidence <= 1
        ):
            raise ValueError(
                "Confidence must be a number greater than 0 "
                "and less than or equal to 1."
            )

        folder_result = self.folder_processor.process(
            uploaded_files
        )

        per_image = []
        aggregated = defaultdict(list)

        with TemporaryDirectory() as temp_dir:

            temp_dir = Path(temp_dir)

            for index, image_data in enumerate(
                folder_result["valid_images"],
                start=1,
            ):
                original_filename = image_data["filename"]

                suffix = Path(
                    original_filename
                ).suffix.lower()

                temporary_path = (
                    temp_dir / f"image_{index}{suffix}"
                )

                image_data["image"].save(temporary_path)

                detections = self.ingredient_detector.detect(
                    temporary_path,
                    confidence=confidence,
                )

                per_image.append({
                    "filename": original_filename,
                    "detections": detections,
                })

                for detection in detections:
                    label = detection["label"]

                    aggregated[label].append({
                        "filename": original_filename,
                        "confidence": detection["confidence"],
                        "box": detection["box"],
                    })

        ingredients = []

        for label, observations in aggregated.items():

            scores = [
                item["confidence"]
                for item in observations
            ]

            ingredients.append({
                "label": label,
                "detection_count": len(observations),
                "image_count": len({
                    item["filename"]
                    for item in observations
                }),
                "max_confidence": round(max(scores), 4),
                "average_confidence": round(
                    sum(scores) / len(scores),
                    4,
                ),
                "observations": observations,
            })

        ingredients.sort(
            key=lambda item: item["label"].casefold()
        )

        return {
            "per_image": per_image,
            "ingredients": ingredients,
            "skipped_files": folder_result["skipped_files"],
            "total_files": folder_result["total_files"],
            "total_images": len(folder_result["valid_images"]),
            "successful_images": len(per_image),
        }
