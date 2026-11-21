
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RECIPE_FILE = (
    BASE_DIR
    / "data"
    / "recipes"
    / "lebanese_recipes_enriched.json"
)

TARGETS = {
    "LB017": [1],
    "LB020": [7, 8],
    "LB022": [0],
    "LB025": [0],
    "LB027": [7],
    "LB033": [0],
    "LB034": [0],
    "LB039": [4],
    "LB041": [8],
}

def load_recipes():
    with RECIPE_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict):
        return data["recipes"]

    return data


def print_recipe(recipe, target_indices):
    recipe_id = recipe.get("id", "UNKNOWN")
    recipe_name = recipe.get("name_en", "Unknown recipe")

    detailed = recipe.get("ingredients_detailed", [])
    normalized = recipe.get("ingredients_normalized", [])
    instructions = recipe.get("instructions", [])

    print("\n" + "=" * 75)
    print(f"{recipe_id} - {recipe_name}")
    print("=" * 75)

    if len(detailed) != len(normalized):
        print("WARNING: Ingredient arrays have different lengths.")
        print(f"Detailed: {len(detailed)}")
        print(f"Normalized: {len(normalized)}")
        return

    print("\nALL SOURCE INGREDIENTS")
    print("-" * 75)

    for i, (detail, norm) in enumerate(zip(detailed, normalized)):
        marker = " <<< TARGET" if i in target_indices else ""

        print(f"\nIndex: {i}{marker}")
        print(f"Source name: {detail.get('name')}")
        print(f"Quantity: {detail.get('quantity')}")
        print(f"Unit: {detail.get('unit')}")
        print(f"Optional: {detail.get('optional')}")
        print(f"Ingredient ID: {detail.get('ingredient_id')}")
        print(f"Canonical name: {detail.get('canonical_name')}")

        if i in target_indices:
            print("\nNORMALIZATION RECORD")
            print(f"Original: {norm.get('original')}")
            print(f"Status: {norm.get('status')}")
            print(f"ID: {norm.get('id')}")
            print(f"Canonical name: {norm.get('canonical_name')}")
            print(f"Components: {norm.get('components')}")
            print(f"Alternatives: {norm.get('alternatives')}")
            print(f"Mapping note: {norm.get('mapping_note')}")

    print("\nCOOKING INSTRUCTIONS")
    print("-" * 75)

    for i, step in enumerate(instructions):
        if isinstance(step, dict):
            text = step.get("text_en", str(step))
        else:
            text = str(step)

        print(f"{i + 1}. {text}")


def main():
    recipes = load_recipes()

    recipe_lookup = {
        recipe.get("id"): recipe
        for recipe in recipes
    }

    print("=" * 75)
    print("BATCH 7 — READ-ONLY INGREDIENT INSPECTION")
    print("=" * 75)

    for recipe_id, indices in TARGETS.items():
        recipe = recipe_lookup.get(recipe_id)

        if recipe is None:
            print(f"\nWARNING: Recipe not found: {recipe_id}")
            continue

        print_recipe(recipe, indices)

    print("\n" + "=" * 75)
    print("INSPECTION COMPLETED")
    print("No files were modified.")
    print("=" * 75)


if __name__ == "__main__":
    main()
