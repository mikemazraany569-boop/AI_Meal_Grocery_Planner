import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RECIPES_FILE = (
    BASE_DIR / "data" / "recipes" / "lebanese_recipes_enriched.json"
)

DIRECT_MAPPINGS = [
    ("LB002", 3, "pepper"),
    ("LB024", 5, "pepper"),
    ("LB025", 5, "pepper"),
    ("LB028", 7, "pepper"),
    ("LB039", 7, "pepper"),
    ("LB029", 2, "coriander"),
    ("LB030", 3, "coriander"),
]

with RECIPES_FILE.open("r", encoding="utf-8") as f:
    data = json.load(f)

recipes = {
    recipe["id"]: recipe
    for recipe in data["recipes"]
}

print("=" * 75)
print("BATCH 5 — READ-ONLY TARGET INSPECTION")
print("=" * 75)

for recipe_id, index, expected in DIRECT_MAPPINGS:
    recipe = recipes.get(recipe_id)

    print(f"\n{recipe_id} | Index {index} | Expected: {expected}")

    if recipe is None:
        print("ERROR: Recipe not found.")
        continue

    normalized = recipe.get("ingredients_normalized", [])
    detailed = recipe.get("ingredients_detailed", [])

    if index >= len(normalized) or index >= len(detailed):
        print("ERROR: Index outside ingredient arrays.")
        continue

    record = normalized[index]
    detail = detailed[index]

    print("Normalized record:")
    print(json.dumps(record, ensure_ascii=False, indent=2))

    print("Detailed record:")
    print(json.dumps(detail, ensure_ascii=False, indent=2))


print("\n" + "=" * 75)
print("LB007 — COMPOSITE INSPECTION")
print("=" * 75)

recipe = recipes.get("LB007")

if recipe:
    index = 11

    if index < len(recipe.get("ingredients_normalized", [])):
        record = recipe["ingredients_normalized"][index]

        print("Parent record:")
        print(json.dumps(record, ensure_ascii=False, indent=2))
    else:
        print("LB007 index 11 not found.")

print("\nNo files were modified.")