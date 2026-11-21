
from src.normalization.ingredient_normalizer import (
    IngredientNormalizer,
)


class DetectionMapper:
    """Map YOLO labels to canonical ingredient records."""

    def __init__(self, normalizer=None):
        self.normalizer = normalizer or IngredientNormalizer()

    def map_detection(self, detection):

        if not isinstance(detection, dict):
            return None

        label = detection.get("label")

        if not isinstance(label, str) or not label.strip():
            return None

        normalized = self.normalizer.normalize(label.strip())

        if not normalized:
            return {
                "detected_label": label.strip(),
                "ingredient_id": None,
                "canonical_name": None,
                "confidence": detection.get("confidence"),
                "recognized": False,
            }

        return {
            "detected_label": label.strip(),
            "ingredient_id": normalized["id"],
            "canonical_name": normalized["canonical_name"],
            "confidence": detection.get("confidence"),
            "recognized": True,
        }

    def map_detections(self, detections):

        if not isinstance(detections, list):
            raise TypeError("detections must be a list")

        mapped = []

        for detection in detections:
            result = self.map_detection(detection)

            if result is not None:
                mapped.append(result)

        return mapped

    def map_folder_result(self, folder_result):

        if not isinstance(folder_result, dict):
            raise TypeError(
                "folder_result must be a dictionary"
            )

        ingredients = folder_result.get("ingredients", [])

        if not isinstance(ingredients, list):
            raise ValueError(
                "folder_result['ingredients'] must be a list"
            )

        mapped = []

        for ingredient in ingredients:
            result = self.map_detection(ingredient)

            if result is None:
                continue

            result["detection_count"] = ingredient.get(
                "detection_count", 0
            )
            result["image_count"] = ingredient.get(
                "image_count", 0
            )
            result["max_confidence"] = ingredient.get(
                "max_confidence"
            )
            result["observations"] = ingredient.get(
                "observations", []
            )

            mapped.append(result)

        return {
            "recognized": [
                item for item in mapped
                if item["recognized"]
            ],
            "unrecognized": [
                item for item in mapped
                if not item["recognized"]
            ],
        }
