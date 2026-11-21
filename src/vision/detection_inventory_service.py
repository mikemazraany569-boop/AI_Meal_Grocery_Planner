
from src.vision.folder_ingredient_detector import (
    FolderIngredientDetector,
)
from src.vision.detection_mapper import DetectionMapper
from src.inventory.inventory_manager import InventoryManager


class DetectionInventoryService:
    """Connect image detection, ingredient mapping, and inventory."""

    def __init__(
        self,
        folder_detector=None,
        detection_mapper=None,
        inventory_manager=None,
    ):
        self.folder_detector = (
            folder_detector or FolderIngredientDetector()
        )
        self.detection_mapper = (
            detection_mapper or DetectionMapper()
        )
        self.inventory_manager = (
            inventory_manager or InventoryManager()
        )

    def detect_and_map(self, uploaded_files, confidence=0.25):
        """Detect ingredients and prepare them for user review."""

        folder_result = self.folder_detector.process(
            uploaded_files,
            confidence=confidence,
        )

        mapping_result = self.detection_mapper.map_folder_result(
            folder_result
        )

        return {
            "recognized": mapping_result["recognized"],
            "unrecognized": mapping_result["unrecognized"],
            "per_image": folder_result["per_image"],
            "skipped_files": folder_result["skipped_files"],
            "total_files": folder_result["total_files"],
            "total_images": folder_result["total_images"],
            "successful_images": folder_result["successful_images"],
        }

    def add_confirmed_ingredients(self, confirmed_ingredients):
        """
        Add user-confirmed recognized detections to inventory.

        Each item must contain:
            recognized
            canonical_name
            confirmed
            quantity (optional)
            unit (optional)
            expiry_date (optional)
        """

        if not isinstance(confirmed_ingredients, list):
            raise TypeError(
                "confirmed_ingredients must be a list"
            )

        added = []
        rejected = []

        for item in confirmed_ingredients:

            if not isinstance(item, dict):
                rejected.append({
                    "item": item,
                    "reason": "Invalid ingredient record",
                })
                continue

            if item.get("confirmed") is not True:
                rejected.append({
                    "item": item,
                    "reason": "Ingredient was not confirmed",
                })
                continue

            if item.get("recognized") is not True:
                rejected.append({
                    "item": item,
                    "reason": "Ingredient is not recognized",
                })
                continue

            canonical_name = item.get("canonical_name")

            if (
                not isinstance(canonical_name, str)
                or not canonical_name.strip()
            ):
                rejected.append({
                    "item": item,
                    "reason": "Missing canonical ingredient name",
                })
                continue

            success = self.inventory_manager.add_ingredient(
                ingredient=canonical_name,
                quantity=item.get("quantity", 1),
                unit=item.get("unit", "piece"),
                expiry_date=item.get("expiry_date"),
            )

            if success:
                added.append(canonical_name)
            else:
                rejected.append({
                    "item": item,
                    "reason": (
                        "Inventory rejected the ingredient "
                        "(possibly invalid data or duplicate)"
                    ),
                })

        return {
            "added": added,
            "rejected": rejected,
            "inventory": self.inventory_manager.get_inventory_details(),
        }
