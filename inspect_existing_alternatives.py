
import json
from pathlib import Path

recipe_path = Path("data/recipes/lebanese_recipes_enriched.json")
ingredient_path = Path("data/ingredients/ingredients_multilingual.json")

with open(recipe_path, "r", encoding="utf-8") as f:
    recipes = json.load(f)["recipes"]

with open(ingredient_path, "r", encoding="utf-8") as f:
    ingredients = json.load(f)["ingredients"]

print("=" * 65)
print("EXISTING ALTERNATIVE NORMALIZATION STRUCTURES")
print("=" * 65)

found = 0

for recipe in recipes:
    for item in recipe.get("ingredients_normalized", []):
        if item.get("status") == "alternatives" or item.get("alternatives"):
            print(f"\n{recipe['id']} - {recipe['name_en']}")
            print(json.dumps(item, ensure_ascii=False, indent=2))
            found += 1

            if found >= 5:
                break
    if found >= 5:
        break

if found == 0:
    print("No existing alternatives found.")

print("\n" + "=" * 65)
print("POSSIBLE BROTH / STOCK INGREDIENTS")
print("=" * 65)

for ingredient in ingredients:
    names = ingredient.get("names", {})
    all_names = [
        name
        for language_names in names.values()
        for name in language_names
    ]

    if any(
        term in name.lower()
        for name in all_names
        for term in ["broth", "stock"]
    ):
        print(json.dumps(ingredient, ensure_ascii=False, indent=2))
