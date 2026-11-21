
import pytest

from src.planner.grocery_generator import GroceryGenerator


@pytest.fixture
def generator():
    return GroceryGenerator()


def make_recipe(name, ingredients):
    return {
        "id": name.upper(),
        "name_en": name,
        "ingredients_detailed": ingredients,
    }


def make_ingredient(ingredient_id, name, quantity, unit, optional=False):
    return {
        "ingredient_id": ingredient_id,
        "canonical_name": name,
        "quantity": quantity,
        "unit": unit,
        "optional": optional,
    }


def test_single_recipe_missing_ingredient(generator):
    recipe = make_recipe(
        "Mujadara",
        [make_ingredient("ING001", "lentils", 2, "cups")],
    )

    result = generator.generate([recipe], [])

    assert len(result["shopping_list"]) == 1
    assert result["shopping_list"][0]["missing_quantity"] == 2
    assert result["shopping_list"][0]["ingredient_id"] == "ING001"


def test_aggregate_same_ingredient_across_recipes(generator):
    recipes = [
        make_recipe("Recipe A", [
            make_ingredient("ING002", "onion", 2, "pieces")
        ]),
        make_recipe("Recipe B", [
            make_ingredient("ING002", "onion", 3, "pieces")
        ]),
    ]

    result = generator.generate(recipes, [])

    item = result["shopping_list"][0]

    assert item["required_quantity"] == 5
    assert item["missing_quantity"] == 5


def test_partial_inventory(generator):
    recipe = make_recipe(
        "Recipe A",
        [make_ingredient("ING003", "tomato", 5, "pieces")],
    )

    inventory = [{
        "id": "ING003",
        "name": "tomato",
        "quantity": 2,
        "unit": "pieces",
    }]

    result = generator.generate([recipe], inventory)

    assert result["shopping_list"][0]["missing_quantity"] == 3


def test_sufficient_inventory(generator):
    recipe = make_recipe(
        "Recipe A",
        [make_ingredient("ING004", "rice", 2, "kg")],
    )

    inventory = [{
        "id": "ING004",
        "name": "rice",
        "quantity": 3,
        "unit": "kg",
    }]

    result = generator.generate([recipe], inventory)

    assert result["shopping_list"] == []


def test_optional_ingredient_excluded(generator):
    recipe = make_recipe(
        "Recipe A",
        [make_ingredient("ING005", "sumac", 1, "tsp", True)],
    )

    result = generator.generate([recipe], [])

    assert result["shopping_list"] == []
    assert len(result["optional_ingredients"]) == 1


def test_unresolved_ingredient(generator):
    recipe = make_recipe(
        "Recipe A",
        [make_ingredient(None, "unknown", 2, "pieces")],
    )

    result = generator.generate([recipe], [])

    assert len(result["review_items"]) == 1
    assert result["review_items"][0]["reason"] == "Unresolved ingredient ID"


def test_unknown_quantity(generator):
    recipe = make_recipe(
        "Recipe A",
        [make_ingredient("ING006", "pepper", "a little", "tsp")],
    )

    result = generator.generate([recipe], [])

    assert len(result["review_items"]) == 1
    assert result["review_items"][0]["reason"] == (
        "Unknown or ambiguous quantity/unit"
    )


def test_incompatible_units_across_recipes(generator):
    recipes = [
        make_recipe("Recipe A", [
            make_ingredient("ING007", "flour", 2, "kg")
        ]),
        make_recipe("Recipe B", [
            make_ingredient("ING007", "flour", 2, "pieces")
        ]),
    ]

    result = generator.generate(recipes, [])

    assert result["shopping_list"] == []
    assert any(
        item["reason"] == "Incompatible units across selected recipes"
        for item in result["review_items"]
    )


def test_empty_recipes(generator):
    result = generator.generate([], [])

    assert result["shopping_list"] == []
    assert result["review_items"] == []
    assert result["optional_ingredients"] == []
    assert result["summary"]["recipes_processed"] == 0


def test_multiple_inventory_records(generator):
    recipe = make_recipe(
        "Recipe A",
        [make_ingredient("ING008", "tomato", 5, "pieces")],
    )

    inventory = [
        {
            "id": "ING008",
            "name": "tomato",
            "quantity": 2,
            "unit": "pieces",
        },
        {
            "id": "ING008",
            "name": "tomato",
            "quantity": 1,
            "unit": "pieces",
        },
    ]

    result = generator.generate([recipe], inventory)

    assert result["shopping_list"][0]["available_quantity"] == 3
    assert result["shopping_list"][0]["missing_quantity"] == 2


def test_aggregate_convertible_units_across_recipes(generator):
    recipes = [
        make_recipe("Recipe A", [
            make_ingredient("ING010", "flour", 500, "g")
        ]),
        make_recipe("Recipe B", [
            make_ingredient("ING010", "flour", 1, "kg")
        ]),
    ]

    result = generator.generate(recipes, [])

    item = result["shopping_list"][0]

    assert item["required_quantity"] == 1500
    assert item["unit"] == "g"
    assert item["missing_quantity"] == 1500


def test_incompatible_inventory_units_are_sent_for_review(generator):
    recipe = make_recipe(
        "Onion recipe",
        [make_ingredient("ING011", "onion", 5, "pieces")],
    )

    inventory = [
        {
            "id": "ING011",
            "name": "onion",
            "quantity": 3,
            "unit": "pieces",
        },
        {
            "id": "ING011",
            "name": "onion",
            "quantity": 1,
            "unit": "bunches",
        },
    ]

    result = generator.generate([recipe], inventory)

    assert result["shopping_list"] == []

    assert any(
        item["ingredient_id"] == "ING011"
        and item["reason"] == "incompatible_unit"
        for item in result["review_items"]
    )


def test_review_items_are_not_added_to_shopping_list(generator):
    recipe = make_recipe(
        "Recipe A",
        [
            make_ingredient("ING012", "pepper", "a little", "tsp"),
            make_ingredient("ING013", "salt", 2, "tsp"),
        ],
    )

    result = generator.generate([recipe], [])

    assert len(result["shopping_list"]) == 1
    assert result["shopping_list"][0]["ingredient_id"] == "ING013"

    assert any(
        item["ingredient_id"] == "ING012"
        for item in result["review_items"]
    )
