
import json
from pathlib import Path

path = Path("data/recipes/lebanese_recipes_enriched.json")

with path.open("r", encoding="utf-8") as file:
    data = json.load(file)

target_ids = ["LB011", "LB013", "LB026", "LB029"]

for recipe in data["recipes"]:
    if recipe["id"] not in target_ids:
        continue

    print(f"\n{'=' * 55}")
    print(recipe["id"], "-", recipe["name_en"])

    for item in recipe.get("ingredients_detailed", []):
        if item.get("ingredient_id") is None:
            print(json.dumps(item, ensure_ascii=False, indent=2))
