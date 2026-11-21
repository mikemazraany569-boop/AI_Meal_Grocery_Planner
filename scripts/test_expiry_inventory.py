
from datetime import date, timedelta

from src.inventory.inventory_manager import InventoryManager


def main():
    inventory = InventoryManager()

    inventory.add_ingredient(
        "eggplant",
        quantity=2,
        unit="pieces",
        expiry_date=(date.today() + timedelta(days=1)).isoformat()
    )

    inventory.add_ingredient(
        "tahini",
        quantity=100,
        unit="grams",
        expiry_date=(date.today() + timedelta(days=30)).isoformat()
    )

    inventory.add_ingredient(
        "lemon",
        quantity=3,
        unit="pieces",
        expiry_date=date.today().isoformat()
    )

    expiring = inventory.get_expiring_ingredients(within_days=3)

    print("INGREDIENTS EXPIRING WITHIN 3 DAYS")
    print("=" * 40)

    for item in expiring:
        print(item)

    expiring_ids = [
        item["id"]
        for item in expiring
        if item["id"] is not None
    ]

    print("\nEXPIRING INGREDIENT IDS")
    print(expiring_ids)


if __name__ == "__main__":
    main()
