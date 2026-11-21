
import json
from pathlib import Path

from src.recipe.recipe_validator import RecipeValidator


class RecipeLoader:
    def __init__(self, file_path=None, ingredient_path=None):
        project_root = Path(__file__).resolve().parents[2]

        if file_path is None:
            file_path = (
                project_root
                / "data"
                / "recipes"
                / "lebanese_recipes_enriched_batch1.json"
            )

        if ingredient_path is None:
            ingredient_path = (
                project_root
                / "data"
                / "ingredients"
                / "ingredients_multilingual.json"
            )

        self.file_path = Path(file_path)
        self.ingredient_path = Path(ingredient_path)
        self.validator = RecipeValidator()

    @staticmethod
    def build_ingredient_groups(ingredients_normalized):
        """
        Convert normalized recipe ingredients into ingredient ID groups.

        Each group represents one required ingredient.
        Alternative ingredients belong to the same group.
        """

        groups = []

        for ingredient in ingredients_normalized or []:
            if not isinstance(ingredient, dict):
                continue

            ids = []

            for component in ingredient.get("components", []):
                if not isinstance(component, dict):
                    continue

                ingredient_id = component.get("id")

                if ingredient_id:
                    ids.append(ingredient_id)

            for alternative in ingredient.get("alternatives", []):
                if not isinstance(alternative, dict):
                    continue

                ingredient_id = alternative.get("id")

                if ingredient_id:
                    ids.append(ingredient_id)

            unique_ids = list(dict.fromkeys(ids))

            if unique_ids:
                groups.append(unique_ids)

        return groups

    def load_recipes(self):
        """Load and validate enriched Lebanese recipes."""

        if not self.file_path.exists():
            raise FileNotFoundError(
                f"Recipe database not found: {self.file_path}"
            )

        if not self.ingredient_path.exists():
            raise FileNotFoundError(
                f"Ingredient database not found: {self.ingredient_path}"
            )

        with self.file_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        with self.ingredient_path.open("r", encoding="utf-8") as file:
            ingredient_data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Recipe database must be a JSON object.")

        if not isinstance(ingredient_data, dict):
            raise ValueError("Ingredient database must be a JSON object.")

        recipes = data.get("recipes", data.get("dishes"))
        ingredients = ingredient_data.get("ingredients")

        if not isinstance(recipes, list) or not recipes:
            raise ValueError(
                "Recipe database must contain a non-empty recipes or dishes list."
            )

        if not isinstance(ingredients, list) or not ingredients:
            raise ValueError(
                "Ingredient database must contain a non-empty ingredients list."
            )

        ingredient_ids = {
            item["id"]
            for item in ingredients
            if isinstance(item, dict) and item.get("id")
        }

        result = self.validator.validate(
            recipes=recipes,
            valid_ingredient_ids=ingredient_ids,
            ingredient_database=ingredients,
        )

        if not result["valid"]:
            error_details = "\n".join(result["errors"])
            raise ValueError(
                f"Recipe validation failed:\n{error_details}"
            )

        if result["warnings"]:
            print("Recipe validation warnings:")
            for warning in result["warnings"]:
                print(f"- {warning}")

        # Add runtime ingredient groups for inventory-based retrieval.
        # The original JSON file is not modified.
        for recipe in recipes:
            recipe["ingredient_groups"] = (
                self.build_ingredient_groups(
                    recipe.get("ingredients_normalized", [])
                )
            )

        return recipes
