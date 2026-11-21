
import json
from pathlib import Path

path = Path("data/recipes/lebanese_recipes_enriched.json")

with path.open(encoding="utf-8") as f:
    data = json.load(f)

print("REMAINING UNRESOLVED INGREDIENTS")
print("=" * 65)

total = 0

for recipe in data["recipes"]:
    for item in recipe.get("ingredients_detailed", []):
        if item.get("ingredient_id") is None:
            print(f"\n{recipe['id']} - {recipe['name_en']}")
            print("Ingredient:", item["name"])

            total += 1

print("\n" + "=" * 65)
print("Total unresolved detailed entries:", total)
