
import pytest

from src.planner.quantity_matcher import QuantityMatcher


@pytest.fixture
def matcher():
    return QuantityMatcher()


def test_sufficient_same_unit(matcher):
    recipe = {
        "id": "LB001",
        "name": "Moutabal",
        "ingredients_detailed": [
            {
                "ingredient_id": "ING011",
                "name": "eggplant",
                "quantity": 2,
                "unit": "pieces",
                "optional": False,
            }
        ],
    }

    inventory = [
        {
            "id": "ING011",
            "name": "eggplant",
            "quantity": 3,
            "unit": "pieces",
        }
    ]

    result = matcher.match_recipe(recipe, inventory)

    assert result["ingredients"][0]["status"] == "sufficient"
    assert result["ingredients"][0]["missing_quantity"] == 0
    assert result["summary"]["sufficient"] == 1


def test_insufficient_quantity(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING011",
                "name": "eggplant",
                "quantity": 3,
                "unit": "pieces",
                "optional": False,
            }
        ],
    }

    inventory = [
        {
            "id": "ING011",
            "quantity": 2,
            "unit": "pieces",
        }
    ]

    result = matcher.match_recipe(recipe, inventory)

    ingredient = result["ingredients"][0]

    assert ingredient["status"] == "insufficient"
    assert ingredient["missing_quantity"] == 1
    assert result["summary"]["insufficient"] == 1


def test_missing_ingredient(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING011",
                "name": "eggplant",
                "quantity": 2,
                "unit": "pieces",
                "optional": False,
            }
        ],
    }

    result = matcher.match_recipe(recipe, [])

    assert result["ingredients"][0]["status"] == "missing"
    assert result["summary"]["missing"] == 1


def test_mass_unit_conversion(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING004",
                "name": "chickpeas",
                "quantity": 400,
                "unit": "g",
                "optional": False,
            }
        ],
    }

    inventory = [
        {
            "id": "ING004",
            "quantity": 0.5,
            "unit": "kg",
        }
    ]

    result = matcher.match_recipe(recipe, inventory)

    ingredient = result["ingredients"][0]

    assert ingredient["status"] == "sufficient"
    assert ingredient["available_quantity"] == pytest.approx(500)
    assert ingredient["missing_quantity"] == 0


def test_volume_unit_conversion(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING007",
                "name": "olive oil",
                "quantity": 3,
                "unit": "tbsp",
                "optional": False,
            }
        ],
    }

    inventory = [
        {
            "id": "ING007",
            "quantity": 60,
            "unit": "ml",
        }
    ]

    result = matcher.match_recipe(recipe, inventory)

    ingredient = result["ingredients"][0]

    assert ingredient["status"] == "sufficient"
    assert ingredient["available_quantity"] == pytest.approx(4)


def test_mass_to_volume_is_not_supported(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING012",
                "name": "tahini",
                "quantity": 4,
                "unit": "tbsp",
                "optional": False,
            }
        ],
    }

    inventory = [
        {
            "id": "ING012",
            "quantity": 100,
            "unit": "g",
        }
    ]

    result = matcher.match_recipe(recipe, inventory)

    assert (
        result["ingredients"][0]["status"]
        == "incompatible_unit"
    )


def test_unknown_recipe_quantity(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING003",
                "name": "parsley",
                "quantity": None,
                "unit": "a few sprigs",
                "optional": False,
            }
        ],
    }

    inventory = [
        {
            "id": "ING003",
            "quantity": 1,
            "unit": "bunches",
        }
    ]

    result = matcher.match_recipe(recipe, inventory)

    assert (
        result["ingredients"][0]["status"]
        == "unknown_quantity"
    )


def test_unresolved_ingredient(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": None,
                "name": "red pepper or sumac",
                "quantity": 0.5,
                "unit": "tsp",
                "optional": False,
            }
        ],
    }

    result = matcher.match_recipe(recipe, [])

    assert (
        result["ingredients"][0]["status"]
        == "unresolved_ingredient"
    )


def test_optional_ingredients_excluded_from_summary(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING025",
                "name": "yogurt",
                "quantity": 2,
                "unit": "tbsp",
                "optional": True,
            }
        ],
    }

    result = matcher.match_recipe(recipe, [])

    assert result["ingredients"][0]["status"] == "missing"
    assert result["summary"]["total_required"] == 0
    assert result["summary"]["missing"] == 0
    assert result["summary"]["optional_ingredients"] == 1


def test_quantity_range_is_unknown(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING001",
                "name": "tomato",
                "quantity": "4-6",
                "unit": "pieces",
                "optional": False,
            }
        ],
    }

    inventory = [
        {
            "id": "ING001",
            "quantity": 5,
            "unit": "pieces",
        }
    ]

    result = matcher.match_recipe(recipe, inventory)

    assert (
        result["ingredients"][0]["status"]
        == "unknown_quantity"
    )


def test_inventory_records_are_aggregated(matcher):
    recipe = {
        "ingredients_detailed": [
            {
                "ingredient_id": "ING004",
                "name": "chickpeas",
                "quantity": 400,
                "unit": "g",
                "optional": False,
            }
        ],
    }

    inventory = [
        {"id": "ING004", "quantity": 200, "unit": "g"},
        {"id": "ING004", "quantity": 0.25, "unit": "kg"},
    ]

    result = matcher.match_recipe(recipe, inventory)

    ingredient = result["ingredients"][0]

    assert ingredient["status"] == "sufficient"
    assert ingredient["available_quantity"] == pytest.approx(450)
    assert ingredient["missing_quantity"] == 0

def test_incompatible_inventory_records_require_review():
    from src.planner.quantity_matcher import QuantityMatcher

    matcher = QuantityMatcher()

    recipe = {
        "id": "TEST001",
        "name": "Onion recipe",
        "ingredients_detailed": [
            {
                "ingredient_id": "ING002",
                "canonical_name": "onion",
                "quantity": 5,
                "unit": "pieces",
            }
        ],
    }

    inventory = [
        {
            "id": "ING002",
            "name": "onion",
            "quantity": 3,
            "unit": "pieces",
        },
        {
            "id": "ING002",
            "name": "onion",
            "quantity": 1,
            "unit": "bunches",
        },
    ]

    result = matcher.match_recipe(recipe, inventory)
    ingredient = result["ingredients"][0]

    assert ingredient["status"] == "incompatible_unit"
    assert ingredient["available_quantity"] == 3
    assert ingredient["missing_quantity"] is None