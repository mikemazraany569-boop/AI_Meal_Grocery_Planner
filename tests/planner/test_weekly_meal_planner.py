
import pytest

from src.planner.weekly_meal_planner import WeeklyMealPlanner


# --------------------------------------------------
# MOCK COMPONENTS
# --------------------------------------------------

class MockInventoryManager:
    """Mock inventory manager for planner tests."""

    def __init__(self):
        self.inventory_ids = ["ING001", "ING002", "ING003"]

        self.expiring_ingredients = [
            {
                "id": "ING001",
                "name": "tomato",
                "quantity": 2,
                "unit": "piece",
                "expiry_date": "2026-11-20",
            }
        ]

        self.inventory_details = [
            {
                "id": "ING001",
                "name": "tomato",
                "quantity": 2,
                "unit": "piece",
                "expiry_date": "2026-11-20",
            }
        ]

    def get_inventory_ids(self):
        return self.inventory_ids

    def get_expiring_ingredients(self, within_days=3):
        return self.expiring_ingredients

    def get_inventory_details(self):
        return self.inventory_details


class MockRecipeRetriever:
    """Mock recipe retriever for planner tests."""

    def __init__(self, results=None):
        self.results = results or []
        self.last_search = None

    def search(
        self,
        query,
        top_k=5,
        ingredient_ids=None,
        expiring_ids=None
    ):
        self.last_search = {
            "query": query,
            "top_k": top_k,
            "ingredient_ids": ingredient_ids,
            "expiring_ids": expiring_ids,
        }

        return self.results[:top_k]


class MockGroceryGenerator:
    """Mock grocery generator for planner tests."""

    def __init__(self):
        self.last_recipes = None
        self.last_inventory = None

    def generate(self, recipes, inventory_details):
        self.last_recipes = recipes
        self.last_inventory = inventory_details

        return {
            "shopping_list": [],
            "review_items": [],
            "optional_ingredients": [],
            "summary": {
                "recipes_processed": len(recipes),
                "shopping_items": 0,
                "items_to_review": 0,
                "optional_items": 0,
            },
        }


# --------------------------------------------------
# TEST HELPERS
# --------------------------------------------------

def make_recipe(recipe_id, name):
    """Create a sample Lebanese recipe."""

    return {
        "id": recipe_id,
        "name_en": name,
        "cuisine": "Lebanese",
        "ingredients_detailed": [
            {
                "ingredient_id": "ING001",
                "name": "tomato",
                "quantity": 2,
                "unit": "piece",
                "optional": False,
            }
        ],
        "instructions": ["Prepare the ingredients."],
    }


def make_search_result(
    recipe_id,
    name,
    score=0.9,
    ingredient_coverage=1.0,
    expiry_coverage=1.0,
    cuisine="Lebanese",
    recipe=None,
):
    """Create a mock RecipeRetriever result."""

    if recipe is None:
        recipe = make_recipe(recipe_id, name)

    return {
        "score": score,
        "semantic_score": score,
        "ingredient_coverage": ingredient_coverage,
        "expiry_coverage": expiry_coverage,
        "matched_expiring_groups": 1,
        "missing_required_groups": [],
        "document": f"Recipe: {name}",
        "metadata": {
            "id": recipe_id,
            "name_en": name,
            "cuisine": cuisine,
            "recipe": recipe,
        },
    }


# --------------------------------------------------
# FIXTURES
# --------------------------------------------------

@pytest.fixture
def inventory_manager():
    return MockInventoryManager()


@pytest.fixture
def recipe_results():
    results = [
        make_search_result(
            "LB001",
            "Baba ghanouj",
            score=0.95
        )
    ]

    results.extend(
        make_search_result(
            f"LB{i:03d}",
            f"Lebanese Recipe {i}",
            score=0.9 - (i * 0.05)
        )
        for i in range(2, 9)
    )

    return results

@pytest.fixture
def recipe_retriever(recipe_results):
    return MockRecipeRetriever(recipe_results)


@pytest.fixture
def grocery_generator():
    return MockGroceryGenerator()


@pytest.fixture
def planner(
    recipe_retriever,
    inventory_manager,
    grocery_generator
):
    return WeeklyMealPlanner(
        recipe_retriever=recipe_retriever,
        inventory_manager=inventory_manager,
        grocery_generator=grocery_generator,
    )


# --------------------------------------------------
# INITIALIZATION TESTS
# --------------------------------------------------

def test_planner_initialization(
    recipe_retriever,
    inventory_manager,
    grocery_generator
):
    planner = WeeklyMealPlanner(
        recipe_retriever,
        inventory_manager,
        grocery_generator,
    )

    assert planner.recipe_retriever is recipe_retriever
    assert planner.inventory_manager is inventory_manager
    assert planner.grocery_generator is grocery_generator


def test_default_grocery_generator(
    recipe_retriever,
    inventory_manager
):
    planner = WeeklyMealPlanner(
        recipe_retriever,
        inventory_manager,
    )

    assert planner.grocery_generator is not None


# --------------------------------------------------
# PARAMETER VALIDATION TESTS
# --------------------------------------------------

@pytest.mark.parametrize(
    "days",
    [0, -1, 1.5, "7", True, None]
)
def test_invalid_days(planner, days):
    with pytest.raises(ValueError):
        planner.generate_plan(days=days)


@pytest.mark.parametrize(
    "meals_per_day",
    [0, -1, 1.5, "2", True, None]
)
def test_invalid_meals_per_day(planner, meals_per_day):
    with pytest.raises(ValueError):
        planner.generate_plan(meals_per_day=meals_per_day)


@pytest.mark.parametrize(
    "expiry_window_days",
    [-1, 1.5, "3", True, None]
)
def test_invalid_expiry_window(planner, expiry_window_days):
    with pytest.raises(ValueError):
        planner.generate_plan(
            expiry_window_days=expiry_window_days
        )


@pytest.mark.parametrize(
    "query",
    ["", "   ", None, 123]
)
def test_invalid_query(planner, query):
    with pytest.raises(ValueError):
        planner.generate_plan(query=query)


@pytest.mark.parametrize(
    "top_k",
    [0, -1, 1.5, "5", True]
)
def test_invalid_top_k(planner, top_k):
    with pytest.raises(ValueError):
        planner.generate_plan(top_k=top_k)


# --------------------------------------------------
# INVENTORY INTEGRATION TESTS
# --------------------------------------------------

def test_inventory_data_passed_to_retriever(
    planner,
    recipe_retriever
):
    planner.generate_plan(
        days=2,
        meals_per_day=1,
        expiry_window_days=5,
    )

    assert recipe_retriever.last_search["ingredient_ids"] == [
        "ING001",
        "ING002",
        "ING003",
    ]

    assert recipe_retriever.last_search["expiring_ids"] == [
        "ING001"
    ]

    assert recipe_retriever.last_search["query"] == (
        "Lebanese recipes using available ingredients"
    )


def test_expiry_window_passed_to_inventory(
    planner,
    inventory_manager
):
    # Verify the configured expiry window is used.
    class TrackingInventoryManager(MockInventoryManager):
        def __init__(self):
            super().__init__()
            self.last_expiry_window = None

        def get_expiring_ingredients(self, within_days=3):
            self.last_expiry_window = within_days
            return self.expiring_ingredients

    inventory = TrackingInventoryManager()

    planner = WeeklyMealPlanner(
        MockRecipeRetriever([
            make_search_result("LB001", "Baba ghanouj")
        ]),
        inventory,
        MockGroceryGenerator(),
    )

    planner.generate_plan(
        days=1,
        expiry_window_days=5,
    )

    assert inventory.last_expiry_window == 5


# --------------------------------------------------
# RECIPE SELECTION TESTS
# --------------------------------------------------

def test_select_requested_number_of_recipes(planner):
    result = planner.generate_plan(
        days=3,
        meals_per_day=1,
    )

    assert len(result["selected_recipes"]) == 3
    assert result["summary"]["planned_meals"] == 3


def test_no_recipe_repetition(planner):
    result = planner.generate_plan(
        days=4,
        meals_per_day=1,
    )

    recipe_ids = [
        recipe["id"]
        for recipe in result["selected_recipes"]
    ]

    assert len(recipe_ids) == len(set(recipe_ids))


def test_only_lebanese_recipes_selected(
    recipe_retriever,
    inventory_manager,
    grocery_generator
):
    recipe_retriever.results = [
        make_search_result("LB001", "Baba ghanouj"),
        make_search_result(
            "ME001",
            "Generic Middle Eastern dish",
            cuisine="Middle Eastern",
        ),
        make_search_result(
            "LB002",
            "Fattoush",
            cuisine="Lebanese",
        ),
    ]

    planner = WeeklyMealPlanner(
        recipe_retriever,
        inventory_manager,
        grocery_generator,
    )

    result = planner.generate_plan(
        days=3,
        meals_per_day=1,
    )

    assert [
        recipe["id"]
        for recipe in result["selected_recipes"]
    ] == ["LB001", "LB002"]


def test_recipes_without_original_recipe_are_skipped(
    recipe_retriever,
    inventory_manager,
    grocery_generator
):
    recipe_retriever.results = [
        {
            "score": 0.99,
            "metadata": {
                "id": "LB001",
                "name_en": "Missing original recipe",
                "cuisine": "Lebanese",
            },
        },
        make_search_result("LB002", "Fattoush"),
    ]

    planner = WeeklyMealPlanner(
        recipe_retriever,
        inventory_manager,
        grocery_generator,
    )

    result = planner.generate_plan(days=1)

    assert len(result["selected_recipes"]) == 1
    assert result["selected_recipes"][0]["id"] == "LB002"


def test_duplicate_recipe_ids_are_skipped(
    recipe_retriever,
    inventory_manager,
    grocery_generator
):
    recipe_retriever.results = [
        make_search_result("LB001", "Baba ghanouj"),
        make_search_result("LB001", "Baba ghanouj duplicate"),
        make_search_result("LB002", "Fattoush"),
    ]

    planner = WeeklyMealPlanner(
        recipe_retriever,
        inventory_manager,
        grocery_generator,
    )

    result = planner.generate_plan(
        days=3,
        meals_per_day=1,
    )

    recipe_ids = [
        recipe["id"]
        for recipe in result["selected_recipes"]
    ]

    assert recipe_ids == ["LB001", "LB002"]


# --------------------------------------------------
# WEEKLY PLAN STRUCTURE TESTS
# --------------------------------------------------

def test_weekly_plan_has_correct_number_of_days(planner):
    result = planner.generate_plan(
        days=5,
        meals_per_day=1,
    )

    assert len(result["weekly_plan"]) == 5


def test_meals_are_assigned_to_correct_days(planner):
    result = planner.generate_plan(
        days=3,
        meals_per_day=2,
    )

    assert [
        day["day"]
        for day in result["weekly_plan"]
    ] == [1, 2, 3]

    assert all(
        len(day["meals"]) == 2
        for day in result["weekly_plan"]
    )


def test_multiple_meals_per_day(planner):
    result = planner.generate_plan(
        days=2,
        meals_per_day=2,
    )

    assert result["summary"]["requested_meals"] == 4
    assert result["summary"]["planned_meals"] == 4

    assert len(result["weekly_plan"][0]["meals"]) == 2
    assert len(result["weekly_plan"][1]["meals"]) == 2


def test_meal_numbers_are_sequential(planner):
    result = planner.generate_plan(
        days=2,
        meals_per_day=2,
    )

    for day in result["weekly_plan"]:
        assert [
            meal["meal_number"]
            for meal in day["meals"]
        ] == [1, 2]


# --------------------------------------------------
# INSUFFICIENT RECIPE TESTS
# --------------------------------------------------

def test_fewer_recipes_than_requested(
    recipe_retriever,
    inventory_manager,
    grocery_generator
):
    recipe_retriever.results = [
        make_search_result("LB001", "Baba ghanouj"),
        make_search_result("LB002", "Fattoush"),
    ]

    planner = WeeklyMealPlanner(
        recipe_retriever,
        inventory_manager,
        grocery_generator,
    )

    result = planner.generate_plan(
        days=4,
        meals_per_day=1,
    )

    assert result["summary"]["requested_meals"] == 4
    assert result["summary"]["planned_meals"] == 2
    assert result["summary"]["unfilled_meals"] == 2

    assert len(result["warnings"]) == 1


def test_no_eligible_recipes(
    recipe_retriever,
    inventory_manager,
    grocery_generator
):
    recipe_retriever.results = []

    planner = WeeklyMealPlanner(
        recipe_retriever,
        inventory_manager,
        grocery_generator,
    )

    result = planner.generate_plan(days=2)

    assert result["selected_recipes"] == []
    assert result["summary"]["planned_meals"] == 0
    assert result["summary"]["unfilled_meals"] == 2

    assert len(result["warnings"]) == 2


# --------------------------------------------------
# GROCERY GENERATOR INTEGRATION TESTS
# --------------------------------------------------

def test_grocery_generator_receives_selected_recipes(
    planner,
    grocery_generator
):
    result = planner.generate_plan(
        days=2,
        meals_per_day=1,
    )

    assert grocery_generator.last_recipes == (
        result["selected_recipes"]
    )

    assert len(grocery_generator.last_recipes) == 2


def test_grocery_generator_receives_inventory(
    planner,
    grocery_generator,
    inventory_manager
):
    planner.generate_plan(days=1)

    assert grocery_generator.last_inventory == (
        inventory_manager.inventory_details
    )


def test_grocery_result_is_included_in_plan(planner):
    result = planner.generate_plan(days=2)

    assert "grocery" in result

    assert "shopping_list" in result["grocery"]
    assert "review_items" in result["grocery"]
    assert "optional_ingredients" in result["grocery"]


# --------------------------------------------------
# SUMMARY AND OUTPUT TESTS
# --------------------------------------------------

def test_summary_contains_expected_fields(planner):
    result = planner.generate_plan(
        days=3,
        meals_per_day=1,
    )

    summary = result["summary"]

    assert summary["requested_days"] == 3
    assert summary["requested_meals"] == 3
    assert summary["planned_meals"] == 3
    assert summary["unfilled_meals"] == 0
    assert summary["unique_recipes"] == 3


def test_expiring_ingredients_are_returned(planner):
    result = planner.generate_plan(days=1)

    assert result["expiring_ingredients"] == [
        {
            "id": "ING001",
            "name": "tomato",
            "quantity": 2,
            "unit": "piece",
            "expiry_date": "2026-11-20",
        }
    ]


def test_recipe_details_contain_ranking_scores(planner):
    result = planner.generate_plan(days=2)

    details = result["recipe_details"][0]

    assert details["recipe_id"] == "LB001"
    assert details["recipe_name"] == "Baba ghanouj"
    assert details["score"] == 0.95
    assert details["ingredient_coverage"] == 1.0
    assert details["expiry_coverage"] == 1.0
