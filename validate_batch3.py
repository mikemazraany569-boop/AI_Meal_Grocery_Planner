
import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent

RECIPE_FILE = (
    ROOT / "data" / "recipes"
    / "lebanese_recipes_enriched.json"
)

INGREDIENT_FILE = (
    ROOT / "data" / "ingredients"
    / "ingredients_multilingual.json"
)

BATCH_IDS = {"LB041", "LB042", "LB043", "LB044", "LB045"}

# Load files
with open(RECIPE_FILE, "r", encoding="utf-8") as f:
    recipes = json.load(f)["recipes"]

with open(INGREDIENT_FILE, "r", encoding="utf-8") as f:
    ingredients = json.load(f)["ingredients"]

# Build ID sets
recipe_ids = [r["id"] for r in recipes]
ingredient_ids = {i["id"] for i in ingredients}

recipe_by_id = {r["id"]: r for r in recipes}

errors = []

print("=" * 65)
print("BATCH 3 STRUCTURAL VALIDATION")
print("=" * 65)

# 1. Recipe count and duplicate IDs
print(f"\nTotal recipes: {len(recipes)}")
print(f"Unique recipe IDs: {len(set(recipe_ids))}")

if len(recipe_ids) != len(set(recipe_ids)):
    errors.append("Duplicate recipe IDs detected.")

# 2. Verify all batch recipes exist
missing = BATCH_IDS - set(recipe_by_id)

if missing:
    errors.append(f"Missing batch recipes: {sorted(missing)}")

# 3. Ingredient count and reference validation
for recipe_id in sorted(BATCH_IDS & set(recipe_by_id)):
    recipe = recipe_by_id[recipe_id]

    detailed = recipe.get("ingredients_detailed", [])
    normalized = recipe.get("ingredients_normalized", [])

    print(f"\n{recipe_id} - {recipe['name_en']}")
    print(f"  Detailed ingredients: {len(detailed)}")
    print(f"  Normalized ingredients: {len(normalized)}")

    if len(detailed) != len(normalized):
        errors.append(
            f"{recipe_id}: ingredient count mismatch."
        )

    statuses = Counter()

    for item in normalized:
        status = item.get("status")
        statuses[status] += 1

        if status == "matched":
            for component in item.get("components", []):
                ingredient_id = component.get("ingredient_id")

                if ingredient_id not in ingredient_ids:
                    errors.append(
                        f"{recipe_id}: invalid ingredient ID "
                        f"{ingredient_id}"
                    )

        elif status == "alternatives":
            alternatives = item.get("alternatives", [])

            if len(alternatives) < 2:
                errors.append(
                    f"{recipe_id}: alternatives record has fewer than 2 options."
                )

            for alternative in alternatives:
                ingredient_id = alternative.get("ingredient_id")

                if ingredient_id not in ingredient_ids:
                    errors.append(
                        f"{recipe_id}: invalid alternative ID "
                        f"{ingredient_id}"
                    )

        elif status == "needs_review":
            if recipe_id != "LB041":
                errors.append(
                    f"Unexpected review item in {recipe_id}."
                )

    print(f"  Statuses: {dict(statuses)}")

    # Check instructions
    if not recipe.get("instructions"):
        errors.append(f"{recipe_id}: missing instructions.")

# 4. Verify the two intended unresolved cases
lb041 = recipe_by_id.get("LB041")

if lb041:
    review_names = {
        item["original"]
        for item in lb041.get("ingredients_normalized", [])
        if item.get("status") == "needs_review"
    }

    alternative_names = {
        item["original"]
        for item in lb041.get("ingredients_normalized", [])
        if item.get("status") == "alternatives"
    }

    if "long green peppers" not in review_names:
        errors.append("LB041: long green peppers review record missing.")

    if "minced lamb or beef" not in alternative_names:
        errors.append("LB041: meat alternatives record missing.")

# Final report
print("\n" + "=" * 65)

if errors:
    print("VALIDATION FAILED")
    for error in errors:
        print("ERROR:", error)
else:
    print("ALL CHECKS PASSED")

print("=" * 65)
