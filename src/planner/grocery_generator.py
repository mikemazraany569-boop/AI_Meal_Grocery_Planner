
from collections import defaultdict

from src.planner.quantity_matcher import QuantityMatcher


class GroceryGenerator:
    """Generate a combined grocery list from selected recipes."""

    def __init__(self, quantity_matcher=None):
        self.matcher = quantity_matcher or QuantityMatcher()

    def generate(self, recipes, inventory_details):
        """
        Generate missing grocery quantities for multiple recipes.

        Returns:
            {
                "shopping_list": [...],
                "review_items": [...],
                "optional_ingredients": [...]
            }
        """
        grouped = defaultdict(list)
        review_items = []
        optional_ingredients = []

        # Step 1: Collect ingredient requirements.
        for recipe in recipes:
            recipe_name = (
                recipe.get("name_en")
                or recipe.get("name")
                or "Unnamed recipe"
            )

            for ingredient in recipe.get("ingredients_detailed", []):
                ingredient_id = ingredient.get("ingredient_id")
                name = (
                    ingredient.get("canonical_name")
                    or ingredient.get("name")
                    or "Unknown ingredient"
                )

                item = {
                    "ingredient_id": ingredient_id,
                    "ingredient_name": name,
                    "quantity": ingredient.get("quantity"),
                    "unit": ingredient.get("unit"),
                    "optional": bool(ingredient.get("optional", False)),
                    "recipe_name": recipe_name,
                }

                if item["optional"]:
                    optional_ingredients.append(item)
                    continue

                if ingredient_id is None:
                    review_items.append({
                        **item,
                        "reason": "Unresolved ingredient ID",
                    })
                    continue

                quantity = self.matcher.parse_quantity(item["quantity"])
                unit = self.matcher.normalize_unit(item["unit"])

                if quantity is None or unit is None:
                    review_items.append({
                        **item,
                        "reason": "Unknown or ambiguous quantity/unit",
                    })
                    continue

                grouped[ingredient_id].append({
                    **item,
                    "quantity": quantity,
                    "unit": unit,
                })

        # Step 2: Aggregate quantities across recipes.
        aggregated = []
        blocked_ids = set()

        for ingredient_id, items in grouped.items():
            first = items[0]
            target_unit = first["unit"]
            total_quantity = 0.0

            for item in items:
                converted = self.matcher.convert_quantity(
                    item["quantity"],
                    item["unit"],
                    target_unit,
                )

                if converted is None:
                    blocked_ids.add(ingredient_id)
                    review_items.append({
                        "ingredient_id": ingredient_id,
                        "ingredient_name": first["ingredient_name"],
                        "reason": (
                            "Incompatible units across selected recipes"
                        ),
                        "recipe_name": item["recipe_name"],
                    })
                    break

                total_quantity += converted

            if ingredient_id not in blocked_ids:
                aggregated.append({
                    "ingredient_id": ingredient_id,
                    "canonical_name": first["ingredient_name"],
                    "quantity": total_quantity,
                    "unit": target_unit,
                    "optional": False,
                })

        # Step 3: Compare combined requirements with inventory.
        combined_recipe = {
            "id": "WEEKLY_PLAN",
            "name": "Weekly meal plan",
            "ingredients_detailed": aggregated,
        }

        result = self.matcher.match_recipe(
            combined_recipe,
            inventory_details,
        )

        # Step 4: Build the shopping list.
        shopping_list = []

        for ingredient in result["ingredients"]:
            status = ingredient["status"]

            if status in ("missing", "insufficient"):
                missing_quantity = ingredient["missing_quantity"]

                if status == "missing":
                    missing_quantity = ingredient["required_quantity"]

                shopping_list.append({
                    "ingredient_id": ingredient["ingredient_id"],
                    "ingredient_name": ingredient["ingredient_name"],
                    "required_quantity": ingredient["required_quantity"],
                    "available_quantity": (
                        ingredient["available_quantity"] or 0
                    ),
                    "missing_quantity": missing_quantity,
                    "unit": ingredient["required_unit"],
                    "status": status,
                })

            elif status != "sufficient":
                review_items.append({
                    "ingredient_id": ingredient["ingredient_id"],
                    "ingredient_name": ingredient["ingredient_name"],
                    "reason": status,
                })

        return {
            "shopping_list": shopping_list,
            "review_items": review_items,
            "optional_ingredients": optional_ingredients,
            "summary": {
                "recipes_processed": len(recipes),
                "shopping_items": len(shopping_list),
                "items_to_review": len(review_items),
                "optional_items": len(optional_ingredients),
            },
        }
