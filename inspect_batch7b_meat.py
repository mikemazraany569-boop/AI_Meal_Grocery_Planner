
import json
from pathlib import Path

# ============================================================
# BATCH 7B — MEAT SOURCE INVESTIGATION
# READ-ONLY: NO FILES WILL BE MODIFIED
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

RECIPE_FILE = (
    BASE_DIR
    / "data"
    / "recipes"
    / "lebanese_recipes_enriched.json"
)

TARGETS = {
    "LB022": "Medium fat meat",
    "LB025": "Meat",
    "LB027": "meat",
    "LB039": "meat",
}

SOURCE_KEYWORDS = (
    "source", "reference", "citation", "document",
    "page", "url", "author", "origin", "attribution"
)

INSTRUCTION_KEYWORDS = ("instruction", "step", "method")
INGREDIENT_KEYWORDS = ("ingredient",)


def print_section(title):
    print("\n" + "=" * 75)
    print(title)
    print("=" * 75)


def find_relevant_fields(obj, path=""):
    """Recursively display ingredient, instruction and source fields."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            key_lower = key.lower()

            if any(word in key_lower for word in (
                INGREDIENT_KEYWORDS
                + INSTRUCTION_KEYWORDS
                + SOURCE_KEYWORDS
            )):
                print(f"\n[{current_path}]")
                print(json.dumps(value, indent=2, ensure_ascii=False))

            elif isinstance(value, (dict, list)):
                find_relevant_fields(value, current_path)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            find_relevant_fields(value, f"{path}[{index}]")


def main():
    if not RECIPE_FILE.exists():
        print(f"ERROR: Recipe file not found:\n{RECIPE_FILE}")
        return

    with RECIPE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    recipes = data.get("recipes", [])

    if not isinstance(recipes, list):
        print("ERROR: Expected a list under the 'recipes' key.")
        return

    print_section("BATCH 7B — READ-ONLY INVESTIGATION")
    print(f"Recipe file: {RECIPE_FILE}")
    print(f"Total recipes loaded: {len(recipes)}")
    print("Modification mode: DISABLED")

    recipes_by_id = {
        recipe.get("id"): recipe
        for recipe in recipes
        if isinstance(recipe, dict)
    }

    for recipe_id, target_ingredient in TARGETS.items():
        print_section(
            f"{recipe_id} — TARGET: {target_ingredient}"
        )

        recipe = recipes_by_id.get(recipe_id)

        if recipe is None:
            print("ERROR: Recipe not found.")
            continue

        print("Recipe name:", recipe.get("name_en"))
        print("Recipe ID:", recipe.get("id"))

        print("\n--- SOURCE / REFERENCE / INGREDIENT / INSTRUCTION DATA ---")
        find_relevant_fields(recipe)

        print("\n--- OTHER RECIPE METADATA ---")
        for key, value in recipe.items():
            key_lower = key.lower()

            if not any(word in key_lower for word in (
                INGREDIENT_KEYWORDS
                + INSTRUCTION_KEYWORDS
                + SOURCE_KEYWORDS
            )):
                if not isinstance(value, (dict, list)):
                    print(f"{key}: {value}")

    print_section("INVESTIGATION COMPLETED")
    print("No recipe data was changed.")
    print("No ingredient dictionary was changed.")
    print("No mappings or aliases were created.")


if __name__ == "__main__":
    main()
