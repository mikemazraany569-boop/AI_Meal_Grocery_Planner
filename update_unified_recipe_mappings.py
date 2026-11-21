
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RECIPE_FILE = ROOT / "data/recipes/lebanese_recipes_enriched.json"
INGREDIENT_FILE = ROOT / "data/ingredients/ingredients_multilingual.json"
BACKUP_FILE = ROOT / "data/recipes/lebanese_recipes_enriched_before_mapping_update.json"

# Explicit mappings reviewed against the unresolved ingredient audit.
# Each value is a list because some source entries contain multiple
# ingredients joined by "and".
OVERRIDES = {
    ("LB002", "tomato juice"): ["ING078"],
    ("LB007", "tahini and vinegar"): ["ING012", "ING045"],
    ("LB012", "tomato juice"): ["ING078"],
    ("LB014", "small courgettes"): ["ING076"],
    ("LB014", "salt and black pepper"): ["ING014", "ING015"],
    ("LB016", "salt and sweet pepper, to taste"): ["ING014", "ING064"],
    ("LB016", "7 spices"): ["ING074"],
    ("LB021", "tomato juice"): ["ING078"],
    ("LB022", "tomato juice"): ["ING078"],
    ("LB027", "vine leaves"): ["ING077"],
    ("LB029", "fresh white haricot beans"): ["ING062"],
    ("LB029", "tomato juice"): ["ING078"]
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def is_reference_recipe(recipe):
    sources = recipe.get("source", [])

    if isinstance(sources, dict):
        sources = [sources]

    return any(
        source.get("source_type") == "food_composition_reference"
        for source in sources
        if isinstance(source, dict)
    )


def main():
    if not RECIPE_FILE.exists():
        raise FileNotFoundError(RECIPE_FILE)

    if not INGREDIENT_FILE.exists():
        raise FileNotFoundError(INGREDIENT_FILE)

    # Preserve original database before modification.
    if not BACKUP_FILE.exists():
        shutil.copy2(RECIPE_FILE, BACKUP_FILE)
        print("Backup created:", BACKUP_FILE)
    else:
        print("Existing backup preserved:", BACKUP_FILE)

    recipes_data = load_json(RECIPE_FILE)
    ingredient_data = load_json(INGREDIENT_FILE)

    recipes = recipes_data["recipes"]

    # Build ID -> canonical English name lookup.
    canonical_names = {
        item["id"]: item["names"]["en"][0]
        for item in ingredient_data["ingredients"]
    }

    updated_recipes = 0
    matched_entries = 0
    review_entries = 0

    for recipe in recipes:
        # Do not modify the five previously enriched recipes.
        if not is_reference_recipe(recipe):
            continue

        recipe_id = recipe["id"]
        original_list = recipe.get("ingredients_original", [])
        old_normalized = recipe.get("ingredients_normalized", [])

        normalized_lookup = {
            item.get("original", "").casefold(): item
            for item in old_normalized
        }

        new_detailed = []
        new_normalized = []

        for original in original_list:
            key = (recipe_id, original.casefold())

            if key in OVERRIDES:
                ingredient_ids = OVERRIDES[key]
                components = [
                    {
                        "original": original,
                        "id": ingredient_id,
                        "canonical_name": canonical_names[ingredient_id],
                        "status": "matched"
                    }
                    for ingredient_id in ingredient_ids
                ]

            else:
                previous = normalized_lookup.get(original.casefold(), {})
                previous_components = previous.get("components", [])

                components = [
                    component.copy()
                    for component in previous_components
                    if component.get("status") == "matched"
                    and component.get("id") in canonical_names
                ]

            if components:
                status = "matched"

                for component in components:
                    new_detailed.append({
                        "name": (
                            component["canonical_name"]
                            if len(components) > 1
                            else original
                        ),
                        "quantity": None,
                        "unit": None,
                        "optional": False,
                        "ingredient_id": component["id"],
                        "canonical_name": component["canonical_name"]
                    })

                matched_entries += 1

            else:
                status = "needs_review"

                new_detailed.append({
                    "name": original,
                    "quantity": None,
                    "unit": None,
                    "optional": False,
                    "ingredient_id": None,
                    "canonical_name": None
                })

                review_entries += 1

            new_normalized.append({
                "original": original,
                "components": components,
                "alternatives": [],
                "status": status
            })

        recipe["ingredients_detailed"] = new_detailed
        recipe["ingredients_normalized"] = new_normalized

        updated_recipes += 1

    recipes_data["recipe_count"] = len(recipes)

    save_json(RECIPE_FILE, recipes_data)

    # Reload and verify the saved database.
    verified = load_json(RECIPE_FILE)

    ids = [recipe["id"] for recipe in verified["recipes"]]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate recipe IDs detected!")

    unresolved = sum(
        ingredient.get("ingredient_id") is None
        for recipe in verified["recipes"]
        for ingredient in recipe.get("ingredients_detailed", [])
    )

    print("\n" + "=" * 50)
    print("RECIPE MAPPING UPDATE COMPLETE")
    print("=" * 50)
    print("Recipes in database:", len(verified["recipes"]))
    print("Reference recipes updated:", updated_recipes)
    print("Matched original entries:", matched_entries)
    print("Entries requiring review:", review_entries)
    print("Unresolved detailed entries:", unresolved)
    print("Duplicate IDs:", len(ids) - len(set(ids)))
    print("JSON validation: PASSED")
    print("Output:", RECIPE_FILE)


if __name__ == "__main__":
    main()
