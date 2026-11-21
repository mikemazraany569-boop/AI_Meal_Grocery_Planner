
import pytest

from src.vision.detection_inventory_service import (
    DetectionInventoryService,
)


class FakeFolderDetector:

    def process(self, uploaded_files, confidence=0.25):
        return {
            "ingredients": [
                {
                    "label": "tomato",
                    "detection_count": 2,
                    "image_count": 1,
                    "max_confidence": 0.95,
                    "observations": [],
                }
            ],
            "per_image": [],
            "skipped_files": [],
            "total_files": 1,
            "total_images": 1,
            "successful_images": 1,
        }


class FakeDetectionMapper:

    def map_folder_result(self, folder_result):
        return {
            "recognized": [
                {
                    "detected_label": "tomato",
                    "ingredient_id": "ING001",
                    "canonical_name": "tomato",
                    "recognized": True,
                }
            ],
            "unrecognized": [],
        }


class FakeInventoryManager:

    def __init__(self):
        self.ingredients = []

    def add_ingredient(
        self,
        ingredient,
        quantity=1,
        unit="piece",
        expiry_date=None,
    ):
        if quantity <= 0:
            return False

        if any(
            item["name"] == ingredient
            for item in self.ingredients
        ):
            return False

        self.ingredients.append({
            "name": ingredient,
            "quantity": quantity,
            "unit": unit,
            "expiry_date": expiry_date,
        })

        return True

    def get_inventory_details(self):
        return [item.copy() for item in self.ingredients]


@pytest.fixture
def service():
    inventory = FakeInventoryManager()

    service = DetectionInventoryService(
        folder_detector=FakeFolderDetector(),
        detection_mapper=FakeDetectionMapper(),
        inventory_manager=inventory,
    )

    return service, inventory


def test_detect_and_map_returns_recognized_ingredients(service):
    service, _ = service

    result = service.detect_and_map(["tomato.jpg"])

    assert len(result["recognized"]) == 1
    assert result["recognized"][0]["canonical_name"] == "tomato"


def test_detect_and_map_returns_unrecognized_ingredients(service):
    service, _ = service

    result = service.detect_and_map(["tomato.jpg"])

    assert result["unrecognized"] == []


def test_detect_and_map_preserves_image_information(service):
    service, _ = service

    result = service.detect_and_map(["tomato.jpg"])

    assert result["total_images"] == 1
    assert result["successful_images"] == 1
    assert result["skipped_files"] == []


def test_confirmed_ingredient_is_added_to_inventory(service):
    service, inventory = service

    result = service.add_confirmed_ingredients([
        {
            "recognized": True,
            "confirmed": True,
            "canonical_name": "tomato",
            "quantity": 3,
            "unit": "piece",
        }
    ])

    assert result["added"] == ["tomato"]
    assert len(inventory.ingredients) == 1
    assert inventory.ingredients[0]["quantity"] == 3


def test_unconfirmed_ingredient_is_not_added(service):
    service, inventory = service

    result = service.add_confirmed_ingredients([
        {
            "recognized": True,
            "confirmed": False,
            "canonical_name": "tomato",
        }
    ])

    assert result["added"] == []
    assert len(inventory.ingredients) == 0
    assert len(result["rejected"]) == 1


def test_unrecognized_ingredient_is_not_added(service):
    service, inventory = service

    result = service.add_confirmed_ingredients([
        {
            "recognized": False,
            "confirmed": True,
            "canonical_name": "unknown",
        }
    ])

    assert result["added"] == []
    assert len(inventory.ingredients) == 0


def test_duplicate_ingredient_is_rejected(service):
    service, _ = service

    ingredient = {
        "recognized": True,
        "confirmed": True,
        "canonical_name": "tomato",
    }

    first = service.add_confirmed_ingredients([ingredient])
    second = service.add_confirmed_ingredients([ingredient])

    assert first["added"] == ["tomato"]
    assert second["added"] == []
    assert len(second["rejected"]) == 1


def test_invalid_quantity_is_rejected(service):
    service, inventory = service

    result = service.add_confirmed_ingredients([
        {
            "recognized": True,
            "confirmed": True,
            "canonical_name": "tomato",
            "quantity": -2,
        }
    ])

    assert result["added"] == []
    assert len(result["rejected"]) == 1
    assert inventory.ingredients == []


def test_expiry_date_is_preserved(service):
    service, inventory = service

    result = service.add_confirmed_ingredients([
        {
            "recognized": True,
            "confirmed": True,
            "canonical_name": "tomato",
            "quantity": 2,
            "unit": "piece",
            "expiry_date": "2026-11-25",
        }
    ])

    assert result["added"] == ["tomato"]
    assert inventory.ingredients[0]["expiry_date"] == "2026-11-25"


def test_invalid_input_type_raises_error(service):
    service, _ = service

    with pytest.raises(TypeError):
        service.add_confirmed_ingredients("tomato")


def test_invalid_ingredient_record_is_rejected(service):
    service, inventory = service

    result = service.add_confirmed_ingredients([
        "tomato"
    ])

    assert result["added"] == []
    assert len(result["rejected"]) == 1
    assert inventory.ingredients == []
