
import re
from collections import defaultdict


class QuantityMatcher:
    """
    Compare recipe ingredient quantities with available inventory.

    Supports safe conversions within mass and volume units.
    Does not estimate missing quantities or convert mass to volume.
    Flags incompatible inventory units for manual review.
    """

    UNIT_GROUPS = {
        "mass": {
            "mg": 0.001,
            "g": 1.0,
            "kg": 1000.0,
        },
        "volume": {
            "ml": 1.0,
            "l": 1000.0,
            "tsp": 5.0,
            "tbsp": 15.0,
            "cup": 240.0,
        },
    }

    UNIT_ALIASES = {
        "milligram": "mg",
        "milligrams": "mg",
        "gram": "g",
        "grams": "g",
        "kilogram": "kg",
        "kilograms": "kg",

        "milliliter": "ml",
        "milliliters": "ml",
        "millilitre": "ml",
        "millilitres": "ml",
        "liter": "l",
        "liters": "l",
        "litre": "l",
        "litres": "l",

        "teaspoon": "tsp",
        "teaspoons": "tsp",
        "tablespoon": "tbsp",
        "tablespoons": "tbsp",

        "cups": "cup",

        "piece": "pieces",
        "pieces": "pieces",
        "lemon": "pieces",
        "lemons": "pieces",

        "clove": "cloves",
        "cloves": "cloves",

        "bunch": "bunches",
        "bunches": "bunches",

        "stalk": "stalks",
        "stalks": "stalks",
    }

    def normalize_unit(self, unit):
        """Normalize common unit names and abbreviations."""

        if unit is None:
            return None

        normalized = str(unit).strip().lower()
        normalized = re.sub(r"\s+", " ", normalized)

        return self.UNIT_ALIASES.get(normalized, normalized)

    def parse_quantity(self, quantity):
        """
        Return a numeric quantity when the value is unambiguous.

        Examples:
            2       -> 2.0
            "2.5"   -> 2.5
            "4-6"   -> None
            "a few" -> None
            None    -> None
        """

        if isinstance(quantity, bool) or quantity is None:
            return None

        if isinstance(quantity, (int, float)):
            return float(quantity)

        value = str(quantity).strip()

        # Accept only a single ordinary numeric value.
        if not re.fullmatch(r"\d+(?:\.\d+)?", value):
            return None

        return float(value)

    def convert_quantity(self, quantity, from_unit, to_unit):
        """
        Convert between compatible units.

        Returns None when conversion is unsupported.
        """

        from_unit = self.normalize_unit(from_unit)
        to_unit = self.normalize_unit(to_unit)

        if from_unit is None or to_unit is None:
            return None

        if from_unit == to_unit:
            return float(quantity)

        for group in self.UNIT_GROUPS.values():
            if from_unit in group and to_unit in group:
                base_quantity = float(quantity) * group[from_unit]
                return base_quantity / group[to_unit]

        return None

    def _prepare_inventory(self, inventory_details):
        """
        Index inventory records by canonical ingredient ID.

        Expected record:
        {
            "id": "ING011",
            "name": "eggplant",
            "quantity": 2,
            "unit": "pieces"
        }
        """

        inventory_by_id = defaultdict(list)

        for item in inventory_details:
            ingredient_id = item.get("id")

            if ingredient_id is None:
                continue

            inventory_by_id[ingredient_id].append(item)

        return inventory_by_id

    def match_recipe(self, recipe, inventory_details):
        """
        Compare one recipe against the available inventory.

        Expected recipe structure:
            recipe["ingredients_detailed"]

        Returns ingredient-level results and a required-ingredient summary.
        """

        inventory_by_id = self._prepare_inventory(inventory_details)

        ingredient_results = []

        for ingredient in recipe.get("ingredients_detailed", []):

            ingredient_id = ingredient.get("ingredient_id")

            ingredient_name = (
                ingredient.get("canonical_name")
                or ingredient.get("name")
                or "Unknown ingredient"
            )

            required_quantity = self.parse_quantity(
                ingredient.get("quantity")
            )

            required_unit = self.normalize_unit(
                ingredient.get("unit")
            )

            is_optional = bool(
                ingredient.get("optional", False)
            )

            result = {
                "ingredient_id": ingredient_id,
                "ingredient_name": ingredient_name,
                "required_quantity": required_quantity,
                "required_unit": required_unit,
                "available_quantity": None,
                "available_unit": None,
                "missing_quantity": None,
                "status": None,
                "optional": is_optional,
            }

            # Check ingredient identification.
            if ingredient_id is None:
                result["status"] = "unresolved_ingredient"
                ingredient_results.append(result)
                continue

            inventory_items = inventory_by_id.get(
                ingredient_id, []
            )

            # No inventory records found.
            if not inventory_items:
                result["status"] = "missing"
                ingredient_results.append(result)
                continue

            # Check required quantity and unit.
            if required_quantity is None or required_unit is None:
                result["status"] = "unknown_quantity"
                ingredient_results.append(result)
                continue

            total_available = 0.0
            compatible_items = 0
            incompatible_items = 0

            # Compare all inventory records.
            for inventory_item in inventory_items:

                available_quantity = self.parse_quantity(
                    inventory_item.get("quantity")
                )

                available_unit = self.normalize_unit(
                    inventory_item.get("unit")
                )

                if (
                    available_quantity is None
                    or available_unit is None
                ):
                    incompatible_items += 1
                    continue

                converted = self.convert_quantity(
                    available_quantity,
                    available_unit,
                    required_unit,
                )

                if converted is None:
                    incompatible_items += 1
                    continue

                total_available += converted
                compatible_items += 1

            # No compatible inventory quantities.
            if compatible_items == 0:

                result["status"] = (
                    "incompatible_unit"
                    if incompatible_items
                    else "unknown_quantity"
                )

                ingredient_results.append(result)
                continue

            result["available_quantity"] = total_available
            result["available_unit"] = required_unit

            # IMPORTANT:
            # If any inventory record is incompatible, do not
            # calculate a definitive missing quantity.
            #
            # This prevents the planner from ignoring inventory
            # records and generating potentially incorrect
            # shopping quantities.
            if incompatible_items > 0:

                result["status"] = "incompatible_unit"

                ingredient_results.append(result)
                continue

            # Calculate the missing quantity.
            missing = max(
                0.0,
                required_quantity - total_available
            )

            result["missing_quantity"] = missing

            if total_available >= required_quantity:
                result["status"] = "sufficient"
            else:
                result["status"] = "insufficient"

            ingredient_results.append(result)

        summary = self._build_summary(ingredient_results)

        return {
            "recipe_id": recipe.get("id"),
            "recipe_name": recipe.get("name"),
            "ingredients": ingredient_results,
            "summary": summary,
        }

    def _build_summary(self, ingredient_results):
        """Summarize required ingredients only."""

        required = [
            item for item in ingredient_results
            if not item["optional"]
        ]

        statuses = [
            "sufficient",
            "insufficient",
            "missing",
            "unknown_quantity",
            "incompatible_unit",
            "unresolved_ingredient",
        ]

        summary = {
            "total_required": len(required),
        }

        for status in statuses:
            summary[status] = sum(
                item["status"] == status
                for item in required
            )

        summary["optional_ingredients"] = sum(
            item["optional"]
            for item in ingredient_results
        )

        return summary
