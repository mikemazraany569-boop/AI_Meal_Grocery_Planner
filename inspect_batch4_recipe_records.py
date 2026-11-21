
import json
from pathlib import Path

path = Path("data/recipes/lebanese_recipes_enriched.json")

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

batch_ids = {f"LB{i:03d}" for i in range(46, 51)}

for recipe in data["recipes"]:
    if recipe["id"] not in batch_ids:
        continue

    print("\n" + "=" * 75)
    print(f"{recipe['id']} - {recipe['name_en']}")
    print("=" * 75)

    detailed = recipe.get("ingredients_detailed", [])
    normalized = recipe.get("ingredients_normalized", [])

    print(f"\nDetailed ingredients: {len(detailed)}")
    for i, ingredient in enumerate(detailed, 1):
        print(f"\n{i}. {json.dumps(ingredient, ensure_ascii=False)}")

    print(f"\nNormalized ingredients: {len(normalized)}")
    for i, ingredient in enumerate(normalized, 1):
        print(f"\n{i}. {json.dumps(ingredient, ensure_ascii=False)}")
