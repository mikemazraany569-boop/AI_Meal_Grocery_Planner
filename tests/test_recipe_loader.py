
import json
import pytest

from src.recipe.recipe_loader import RecipeLoader


def create_test_files(tmp_path, ingredient_id="ING001"):
    recipe = {
        "id": "LB_TEST",
        "name_en": "Test Lebanese recipe",
        "ingredients_original": ["tomato"],
        "ingredients_detailed": [
            {
                "name": "tomato",
                "quantity": 2,
                "unit": "piece",
                "optional": False,
                "ingredient_id": ingredient_id,
                "canonical_name": "tomato",
            }
        ],
        "ingredients_normalized": [
            {
                "original": "tomato",
                "components": [
                    {
                        "original": "tomato",
                        "id": ingredient_id,
                        "canonical_name": "tomato",
                        "status": "matched",
                    }
                ],
                "alternatives": [],
                "status": "matched",
            }
        ],
        "instructions": ["Wash and chop the tomatoes."],
        "source": [
            {
                "name": "Test source",
                "url": "https://example.com",
                "source_type": "test",
            }
        ],
    }

    ingredients = {
        "ingredients": [
            {
                "id": "ING001",
                "names": {
                    "en": ["tomato"],
                    "ar": ["بندورة"],
                    "fr": ["tomate"],
                },
            }
        ]
    }

    recipe_path = tmp_path / "recipes.json"
    ingredient_path = tmp_path / "ingredients.json"

    recipe_path.write_text(
        json.dumps({"recipes": [recipe]}),
        encoding="utf-8",
    )

    ingredient_path.write_text(
        json.dumps(ingredients),
        encoding="utf-8",
    )

    return recipe_path, ingredient_path


def test_load_valid_recipe(tmp_path):
    recipe_path, ingredient_path = create_test_files(tmp_path)

    loader = RecipeLoader(
        file_path=recipe_path,
        ingredient_path=ingredient_path,
    )

    recipes = loader.load_recipes()

    assert len(recipes) == 1
    assert recipes[0]["id"] == "LB_TEST"


def test_reject_unknown_ingredient_id(tmp_path):
    recipe_path, ingredient_path = create_test_files(
        tmp_path,
        ingredient_id="ING999",
    )

    loader = RecipeLoader(
        file_path=recipe_path,
        ingredient_path=ingredient_path,
    )

    with pytest.raises(ValueError, match="Recipe validation failed"):
        loader.load_recipes()
