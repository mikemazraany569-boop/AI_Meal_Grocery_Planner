
from src.inventory.inventory_manager import InventoryManager


def test_add_ingredient_with_quantity():
    inventory = InventoryManager()

    assert inventory.add_ingredient(
        "Tomato",
        quantity=2,
        unit="kg"
    )

    details = inventory.get_inventory_details()

    assert details[0]["name"] == "tomato"
    assert details[0]["quantity"] == 2
    assert details[0]["unit"] == "kg"


def test_add_ingredient_with_expiry_date():
    inventory = InventoryManager()

    assert inventory.add_ingredient(
        "Tomato",
        quantity=3,
        unit="pieces",
        expiry_date="2026-11-15"
    )

    details = inventory.get_inventory_details()

    assert details[0]["expiry_date"] == "2026-11-15"


def test_default_quantity_and_unit():
    inventory = InventoryManager()

    inventory.add_ingredient("Onion")

    details = inventory.get_inventory_details()

    assert details[0]["quantity"] == 1
    assert details[0]["unit"] == "piece"
    assert details[0]["expiry_date"] is None


def test_reject_invalid_quantity():
    inventory = InventoryManager()

    assert inventory.add_ingredient("Tomato", quantity=0) is False
    assert inventory.add_ingredient("Onion", quantity=-2) is False


def test_reject_invalid_expiry_date():
    inventory = InventoryManager()

    assert inventory.add_ingredient(
        "Tomato",
        expiry_date="not-a-date"
    ) is False


def test_inventory_details_returns_copy():
    inventory = InventoryManager()
    inventory.add_ingredient("Tomato")

    details = inventory.get_inventory_details()
    details[0]["quantity"] = 100

    assert inventory.get_inventory_details()[0]["quantity"] == 1
