
from src.inventory.inventory_manager import InventoryManager


def test_same_ingredient_in_different_languages():
    inventory = InventoryManager()

    assert inventory.add_ingredient("Tomato") is True
    assert inventory.add_ingredient("Tomate") is False
    assert inventory.add_ingredient("بندورة") is False

    assert inventory.get_inventory() == ["tomato"]


def test_remove_ingredient_using_another_language():
    inventory = InventoryManager()

    inventory.add_ingredient("Tomato")

    assert inventory.remove_ingredient("بندورة") is True
    assert inventory.get_inventory() == []


def test_unknown_ingredient():
    inventory = InventoryManager()

    assert inventory.add_ingredient("Avocado") is True
    assert inventory.get_inventory() == ["avocado"]


def test_empty_ingredient():
    inventory = InventoryManager()

    assert inventory.add_ingredient("   ") is False
    assert inventory.get_inventory() == []
