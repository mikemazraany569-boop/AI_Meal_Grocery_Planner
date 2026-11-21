
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

recipe_file = (
    ROOT / "data" / "recipes"
    / "lebanese_recipes_enriched.json"
)

ingredient_file = (
    ROOT / "data" / "ingredients"
    / "ingredients_multilingual.json"
)

# Load recipes
with open(recipe_file, "r", encoding="utf-8") as f:
    recipes = json.load(f)["recipes"]

# Load ingredient dictionary
with open(ingredient_file, "r", encoding="utf-8") as f:
    ingredient_data = json.load(f)["ingredients"]

batch_ids = {"LB041", "LB042", "LB043", "LB044", "LB045"}

# Build multilingual lookup
lookup = {}

for ingredient in ingredient_data:
    ingredient_id = ingredient["id"]
    names = ingredient.get("names", {})

    canonical_name = (
        names["en"][0]
        if names.get("en")
        else ingredient_id
    )

    for language in ("en", "ar", "fr"):
        for name in names.get(language, []):
            key = name.strip().lower()

            lookup[key] = {
                "id": ingredient_id,
                "canonical_name": canonical_name
            }

# Diagnostic
print("=" * 65)
print("BATCH 3 INGREDIENT DIAGNOSTIC")
print("=" * 65)

for recipe in recipes:
    if recipe["id"] not in batch_ids:
        continue

    print(f"\n{recipe['id']} - {recipe['name_en']}")

    matched = []
    unmatched = []

    for item in recipe["ingredients_detailed"]:
        name = item["name"].strip().lower()

        if name in lookup:
            matched.append((item["name"], lookup[name]))
        else:
            unmatched.append(item["name"])

    print("Already recognized:", len(matched))

    for name, result in matched:
        print(
            f"  MATCH: {name} -> "
            f"{result['id']} ({result['canonical_name']})"
        )

    print("Needs review:", len(unmatched))

    for name in unmatched:
        print("  REVIEW:", name)

print("\nDIAGNOSTIC FINISHED")
