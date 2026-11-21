
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

path = ROOT / "data" / "recipes" / "lebanese_dishes_reference.json"

with open(path, encoding="utf-8") as file:
    data = json.load(file)

batch_ids = {
    "LB002", "LB003", "LB004",
    "LB006", "LB007", "LB009",
    "LB010", "LB012", "LB013"
}

for recipe in data["dishes"]:
    if recipe.get("id") not in batch_ids:
        continue

    print("\n" + "=" * 65)
    print(recipe["id"], "-", recipe.get("name_en"))
    print("Arabic name:", recipe.get("name_ar"))
    print("Source:", recipe.get("source"))
    print("Source page:", recipe.get("source_page"))
    print("Has quantities:", recipe.get("has_quantities"))
    print("Has instructions:", recipe.get("has_instructions"))

    print("\nOriginal ingredients:")
    for ingredient in recipe.get("ingredients_original", []):
        print("-", ingredient)

    print("\nNormalized ingredients:")
    for ingredient in recipe.get("ingredients_normalized", []):
        print(json.dumps(ingredient, ensure_ascii=False))
