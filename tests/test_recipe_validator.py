
import json
from pathlib import Path

from src.recipe.recipe_validator import RecipeValidator


def test_recipe_batch():
    # Load recipes
    recipe_path = Path(
    "data/recipes/lebanese_recipes_enriched_batch1.json")

    with recipe_path.open("r", encoding="utf-8") as file:
        recipe_data = json.load(file)

    recipes = recipe_data["recipes"]

    # Load ingredients
    ingredient_path = Path(
        "data/ingredients/ingredients_multilingual.json"
    )

    with ingredient_path.open("r", encoding="utf-8") as file:
        ingredient_data = json.load(file)

    ingredients = ingredient_data["ingredients"]

    ingredient_ids = {
        ingredient["id"] for ingredient in ingredients
    }

    # Validate
    validator = RecipeValidator()

    result = validator.validate(
    recipes=recipes,
    valid_ingredient_ids=ingredient_ids,
    ingredient_database=ingredients
)

    print("\nRECIPE VALIDATION REPORT")
    print("=" * 40)
    print("Valid:", result["valid"])
    print("Total recipes:", result["total_recipes"])

    print("\nERRORS:")
    for error in result["errors"]:
        print("-", error)

    print("\nWARNINGS:")
    for warning in result["warnings"]:
        print("-", warning)

    assert result["valid"], (
        "Recipe validation failed: " + str(result["errors"])
    )


if __name__ == "__main__":
    test_recipe_batch()
