
import json
from pathlib import Path

RECIPE_FILE = Path(
    "data/recipes/lebanese_recipes_enriched.json"
)

TARGET_IDS = {
    "LB002", "LB024", "LB025", "LB028",
    "LB029", "LB030", "LB039", "LB041"
}

# Load recipes
with RECIPE_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

# Extract recipe records safely
if isinstance(data, list):
    recipes = data

elif isinstance(data, dict):
    recipes = None

    for key in ("recipes", "dishes"):
        if isinstance(data.get(key), list):
            recipes = data[key]
            break

    if recipes is None:
        raise ValueError(
            "Could not find a 'recipes' or 'dishes' list "
            "in the JSON file."
        )
else:
    raise TypeError(
        f"Unexpected JSON root type: {type(data).__name__}"
    )

# Validate records before processing
if not all(isinstance(recipe, dict) for recipe in recipes):
    raise TypeError(
        "The recipe collection contains non-dictionary records."
    )

# Filter target recipes
target_recipes = [
    recipe for recipe in recipes
    if recipe.get("id") in TARGET_IDS
]

print("=" * 60)
print("RECIPE SELECTION VALIDATION")
print("=" * 60)
print("Total recipes:", len(recipes))
print("Selected recipes:", len(target_recipes))
print("Selected IDs:", [r["id"] for r in target_recipes])

missing_ids = TARGET_IDS - {
    recipe.get("id") for recipe in target_recipes
}

if missing_ids:
    print("Missing target IDs:", sorted(missing_ids))
else:
    print("All target IDs found.")

print("\nRead-only selection completed. No files modified.")
