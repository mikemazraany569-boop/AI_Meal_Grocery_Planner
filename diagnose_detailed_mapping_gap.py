
import json
from pathlib import Path

RECIPE_FILE = Path("data/recipes/lebanese_recipes_enriched.json")

TARGET_IDS = {"LB041", "LB042", "LB043", "LB044", "LB045"}

with RECIPE_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

if isinstance(data, dict):
    recipes = data.get("recipes", data.get("dishes", []))
else:
    recipes = data

print("=" * 65)
print("DETAILED INGREDIENT MAPPING GAP — READ ONLY")
print("=" * 65)

for recipe in recipes:
    if recipe.get("id") not in TARGET_IDS:
        continue

    print(f"\n{recipe['id']} — {recipe.get('name_en')}")

    normalized = recipe.get("ingredients_normalized", [])
    detailed = recipe.get("ingredients_detailed", [])

    normalized_ids = set()

    for item in normalized:
        if not isinstance(item, dict):
            continue

        if item.get("id"):
            normalized_ids.add(item["id"])

        for key in ("components", "alternatives"):
            for candidate in item.get(key, []):
                if isinstance(candidate, dict) and candidate.get("id"):
                    normalized_ids.add(candidate["id"])

    detailed_ids = {
        item.get("ingredient_id")
        for item in detailed
        if isinstance(item, dict) and item.get("ingredient_id")
    }

    print("Normalized records:", len(normalized))
    print("Detailed records:", len(detailed))
    print("Normalized IDs:", sorted(normalized_ids))
    print("Detailed IDs:", sorted(detailed_ids))
    print("Detailed IDs absent from normalized:", sorted(
        detailed_ids - normalized_ids
    ))

    if detailed_ids - normalized_ids:
        print("\nDetailed records requiring investigation:")

        for item in detailed:
            if item.get("ingredient_id") in detailed_ids - normalized_ids:
                print({
                    "name": item.get("name"),
                    "ingredient_id": item.get("ingredient_id"),
                    "optional": item.get("optional", False)
                })

print("\nDiagnostic completed. No files modified.")
