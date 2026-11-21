
import json
from pathlib import Path

path = Path("data/recipes/lebanese_recipes_enriched.json")

with path.open(encoding="utf-8") as f:
    data = json.load(f)

print("UNRESOLVED INGREDIENTS")
print("=" * 60)

count = 0

for recipe in data["recipes"]:
    for ingredient in recipe["ingredients_detailed"]:
        if ingredient.get("ingredient_id") is None:
            print(
                f"{recipe['id']} - {recipe['name_en']}: "
                f"{ingredient['name']}"
            )
            count += 1

print("=" * 60)
print("Total unresolved:", count)
