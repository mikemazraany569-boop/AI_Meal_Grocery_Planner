from src.inventory.inventory_manager import InventoryManager
from src.inventory.text_parser import TextInventoryParser


def test_english_parsing():
    result = TextInventoryParser.parse_ingredients(
        "Tomato, Onion, Parsley"
    )
    assert result == ["Tomato", "Onion", "Parsley"]


def test_french_parsing():
    result = TextInventoryParser.parse_ingredients(
        "Tomate, Oignon, Persil"
    )
    assert result == ["Tomate", "Oignon", "Persil"]


def test_arabic_parsing():
    result = TextInventoryParser.parse_ingredients(
        "بندورة، بصل، بقدونس"
    )
    assert result == ["بندورة", "بصل", "بقدونس"]


def test_add_ingredients():
    inventory = InventoryManager()

    inventory.add_ingredient("Tomato")
    inventory.add_ingredient("Onion")

    assert inventory.get_inventory() == ["tomato", "onion"]


def test_prevent_duplicates():
    inventory = InventoryManager()

    inventory.add_ingredient("Tomato")
    inventory.add_ingredient("Tomato")

    assert inventory.get_inventory() == ["tomato"]


def test_remove_ingredient():
    inventory = InventoryManager()

    inventory.add_ingredient("Tomato")
    inventory.add_ingredient("Onion")
    inventory.remove_ingredient("Onion")

    assert inventory.get_inventory() == ["tomato"]


def test_clear_inventory():
    inventory = InventoryManager()

    inventory.add_ingredient("Tomato")
    inventory.clear_inventory()

    assert inventory.get_inventory() == []