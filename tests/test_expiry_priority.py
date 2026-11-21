
from datetime import date, timedelta

from src.inventory.inventory_manager import InventoryManager


def test_expiring_ingredients_are_prioritized():
    inventory = InventoryManager()

    today = date.today()

    inventory.add_ingredient(
        "Tomato",
        expiry_date=(today + timedelta(days=2)).isoformat()
    )

    inventory.add_ingredient(
        "Onion",
        expiry_date=(today + timedelta(days=1)).isoformat()
    )

    inventory.add_ingredient(
        "Parsley",
        expiry_date=(today + timedelta(days=10)).isoformat()
    )

    result = inventory.get_expiring_ingredients(within_days=3)

    assert [item["name"] for item in result] == [
        "onion",
        "tomato"
    ]


def test_expired_ingredients_are_excluded():
    inventory = InventoryManager()

    yesterday = (date.today() - timedelta(days=1)).isoformat()

    inventory.add_ingredient(
        "Tomato",
        expiry_date=yesterday
    )

    assert inventory.get_expiring_ingredients() == []


def test_ingredients_without_expiry_are_excluded():
    inventory = InventoryManager()

    inventory.add_ingredient("Tomato")

    assert inventory.get_expiring_ingredients() == []
