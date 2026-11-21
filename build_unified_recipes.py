
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent

REFERENCE_FILE = (
    ROOT / "data" / "recipes" / "lebanese_dishes_reference.json"
)

EXISTING_FILE = (
    ROOT / "data" / "recipes" / "lebanese_recipes_enriched_batch1.json"
)

OUTPUT_FILE = (
    ROOT / "data" / "recipes" / "lebanese_recipes_enriched.json"
)


def load_json(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def get_canonical_name(component):
    return component.get("canonical_name")


def convert_to_detailed_ingredients(original, normalized):
    """Convert source ingredient mappings into detailed records."""

    components_by_original = {}

    for item in normalized:
        components_by_original[item.get("original", "").casefold()] = item

    detailed = []

    for ingredient in original:
        normalized_item = components_by_original.get(
            ingredient.casefold(), {}
        )

        components = normalized_item.get("components", [])

        # Only create a directly mapped record when there is
        # exactly one matched canonical ingredient.
        matched = [
            component
            for component in components
            if component.get("status") == "matched"
            and component.get("id")
        ]

        if len(matched) == 1:
            component = matched[0]

            detailed.append({
                "name": ingredient,
                "quantity": None,
                "unit": None,
                "optional": False,
                "ingredient_id": component["id"],
                "canonical_name": get_canonical_name(component)
            })
        else:
            # Preserve unresolved or ambiguous source ingredients.
            detailed.append({
                "name": ingredient,
                "quantity": None,
                "unit": None,
                "optional": False,
                "ingredient_id": None,
                "canonical_name": None
            })

    return detailed


def convert_reference_dish(dish):
    original = dish.get("ingredients_original", [])
    normalized = dish.get("ingredients_normalized", [])

    detailed = convert_to_detailed_ingredients(
        original,
        normalized
    )

    source_name = dish.get(
        "source",
        "Lebanon Food Composition Data"
    )

    source_page = dish.get("source_page")

    source_record = {
        "name": source_name,
        "url": None,
        "source_type": "food_composition_reference",
        "used_for": "Dish name and ingredient list"
    }

    if source_page is not None:
        source_record["source_page"] = source_page

    return {
        "id": dish["id"],
        "name_en": dish.get("name_en"),
        "source_display_name": dish.get("name_en"),
        "name_ar": dish.get("name_ar"),
        "category": None,
        "servings": None,
        "preparation_time_minutes": None,
        "cooking_time_minutes": None,
        "total_time_minutes": None,
        "time_notes": "Not provided by the reference source.",
        "ingredients_original": original,
        "ingredients_detailed": detailed,
        "ingredients_normalized": normalized,
        "instructions": [],
        "source": [source_record],
        "verification_status": "source_checked_name_and_ingredients",
        "notes": [
            "Ingredient quantities are not available in the reference source.",
            "Cooking instructions are not available in the reference source.",
            "Unresolved ingredient mappings require review.",
            "This record can be used for ingredient matching, "
            "but not exact quantity calculations."
        ]
    }


def main():
    print("Loading recipe sources...")

    reference_data = load_json(REFERENCE_FILE)
    existing_data = load_json(EXISTING_FILE)

    reference_dishes = reference_data.get("dishes", [])
    existing_recipes = existing_data.get("recipes", [])

    # Preserve all existing enriched recipes.
    recipes_by_id = {
        recipe["id"]: recipe
        for recipe in existing_recipes
    }

    added = 0
    skipped = 0

    for dish in reference_dishes:
        dish_id = dish.get("id")

        if not dish_id:
            print("Skipping dish without ID.")
            skipped += 1
            continue

        if dish_id in recipes_by_id:
            print(f"Already enriched: {dish_id}")
            skipped += 1
            continue

        recipes_by_id[dish_id] = convert_reference_dish(dish)
        print(f"Added: {dish_id} - {dish.get('name_en')}")
        added += 1

    recipes = sorted(
        recipes_by_id.values(),
        key=lambda recipe: recipe["id"]
    )

    # Check duplicate IDs.
    ids = [recipe["id"] for recipe in recipes]
    duplicates = [
        recipe_id
        for recipe_id, count in Counter(ids).items()
        if count > 1
    ]

    if duplicates:
        raise ValueError(f"Duplicate recipe IDs: {duplicates}")

    output_data = {
        "dataset_name": "Lebanese Recipes Enriched Dataset",
        "language": "en",
        "recipe_count": len(recipes),
        "notes": [
            "Unified Lebanese recipe database.",
            "Existing enriched recipes are preserved.",
            "Unknown quantities are stored as null.",
            "Unavailable instructions are stored as empty lists.",
            "Unresolved ingredient mappings are preserved for review."
        ],
        "recipes": recipes
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            output_data,
            file,
            ensure_ascii=False,
            indent=2
        )

    # Reload to verify valid JSON.
    verified = load_json(OUTPUT_FILE)

    unresolved = sum(
        1
        for recipe in verified["recipes"]
        for ingredient in recipe["ingredients_detailed"]
        if ingredient.get("ingredient_id") is None
    )

    without_instructions = sum(
        1
        for recipe in verified["recipes"]
        if not recipe.get("instructions")
    )

    print("\n" + "=" * 45)
    print("UNIFIED DATABASE CREATED")
    print("=" * 45)
    print("Output:", OUTPUT_FILE)
    print("Existing recipes:", len(existing_recipes))
    print("New recipes added:", added)
    print("Skipped:", skipped)
    print("Total recipes:", len(verified["recipes"]))
    print("Unresolved ingredient entries:", unresolved)
    print("Recipes without instructions:", without_instructions)
    print("Duplicate IDs:", len(duplicates))
    print("JSON validation: PASSED")


if __name__ == "__main__":
    main()
