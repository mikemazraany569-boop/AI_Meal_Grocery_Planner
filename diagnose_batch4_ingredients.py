
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RECIPE_FILE = (
    ROOT / "data" / "recipes"
    / "lebanese_recipes_enriched.json"
)

INGREDIENT_FILE = (
    ROOT / "data" / "ingredients"
    / "ingredients_multilingual.json"
)

BATCH_IDS = {
    "LB046", "LB047", "LB048", "LB049", "LB050"
}

with open(RECIPE_FILE, "r", encoding="utf-8") as f:
    recipes = json.load(f)["recipes"]

with open(INGREDIENT_FILE, "r", encoding="utf-8") as f:
    ingredient_data = json.load(f)["ingredients"]

# Build multilingual lookup
lookup = {}

for ingredient in ingredient_data:
    names = ingredient.get("names", {})
    english_names = names.get("en", [])

    canonical_name = (
        english_names[0] if english_names
        else ingredient["id"]
    )

    for language in ("en", "ar", "fr"):
        for name in names.get(language, []):
            lookup[name.strip().lower()] = {
                "id": ingredient["id"],
                "canonical_name": canonical_name
            }

print("=" * 65)
print("BATCH 4 INGREDIENT DIAGNOSTIC")
print("=" * 65)

total_matched = 0
total_review = 0

for recipe in recipes:
    if recipe["id"] not in BATCH_IDS:
        continue

    matched = []
    unmatched = []

    for item in recipe["ingredients_detailed"]:
        name = item["name"].strip().lower()

        if name in lookup:
            matched.append((item["name"], lookup[name]))
        else:
            unmatched.append(item["name"])

    total_matched += len(matched)
    total_review += len(unmatched)

    print(f"\n{recipe['id']} - {recipe['name_en']}")
    print("Already recognized:", len(matched))

    for name, result in matched:
        print(
            f"  MATCH: {name} -> "
            f"{result['id']} ({result['canonical_name']})"
        )

    print("Needs review:", len(unmatched))

    for name in unmatched:
        print("  REVIEW:", name)

print("\n" + "=" * 65)
print("BATCH 4 SUMMARY")
print("=" * 65)
print("Total recognized:", total_matched)
print("Total requiring review:", total_review)
print("Total ingredient records:", total_matched + total_review)
