
from datetime import date, timedelta

from src.normalization.ingredient_normalizer import IngredientNormalizer

class InventoryManager:
    def __init__(self):
        self.ingredients = []
        self.normalizer = IngredientNormalizer()

    def _prepare_ingredient(self, ingredient):
        if not isinstance(ingredient, str):
            return None

        ingredient = ingredient.strip()

        if not ingredient:
            return None

        result = self.normalizer.normalize(ingredient)

        if result:
            return {
                "id": result["id"],
                "name": result["canonical_name"]
            }

        return {
            "id": None,
            "name": ingredient.casefold()
        }

    def add_ingredient(
        self,
        ingredient,
        quantity=1,
        unit="piece",
        expiry_date=None
    ):
        prepared = self._prepare_ingredient(ingredient)

        if prepared is None:
            return False

        if not isinstance(quantity, (int, float)) or quantity <= 0:
            return False

        if not isinstance(unit, str) or not unit.strip():
            return False

        if expiry_date is not None:
            try:
                date.fromisoformat(expiry_date)
            except (ValueError, TypeError):
                return False

        if any(item["name"] == prepared["name"]
               for item in self.ingredients):
            return False

        self.ingredients.append({
            "id": prepared["id"],
            "name": prepared["name"],
            "quantity": quantity,
            "unit": unit.strip().lower(),
            "expiry_date": expiry_date
        })

        return True

    def remove_ingredient(self, ingredient):
        prepared = self._prepare_ingredient(ingredient)

        if prepared is None:
            return False

        for item in self.ingredients:
            if item["name"] == prepared["name"]:
                self.ingredients.remove(item)
                return True

        return False

    def get_inventory(self):
        return [item["name"] for item in self.ingredients]

    def get_inventory_ids(self):
        """Return unique canonical ingredient IDs from inventory."""

        return list(dict.fromkeys(
        item["id"]
        for item in self.ingredients
        if item["id"] is not None
    ))
    
    def get_inventory_details(self):
        return [item.copy() for item in self.ingredients]

    def get_expiring_ingredients(self, within_days=3):
        """
        Return ingredients expiring within the specified number of days,
        ordered by nearest expiry date.
        """
        if (
            not isinstance(within_days, int)
            or isinstance(within_days, bool)
            or within_days < 0
        ):
            raise ValueError(
                "within_days must be a non-negative integer"
            )

        today = date.today()
        cutoff_date = today + timedelta(days=within_days)

        expiring = []

        for item in self.ingredients:
            expiry = item["expiry_date"]

            if expiry is None:
                continue

            expiry_date = date.fromisoformat(expiry)

            if today <= expiry_date <= cutoff_date:
                expiring.append(item.copy())

        return sorted(
            expiring,
            key=lambda item: item["expiry_date"]
        )

    def clear_inventory(self):
        self.ingredients.clear()
