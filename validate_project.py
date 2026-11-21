
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent

RECIPE_FILE = (
    BASE_DIR / "data" / "recipes" / "lebanese_recipes_enriched.json"
)
INGREDIENT_FILE = (
    BASE_DIR / "data" / "ingredients" / "ingredients_multilingual.json"
)

with RECIPE_FILE.open("r", encoding="utf-8") as f:
    recipes = json.load(f)["recipes"]

with INGREDIENT_FILE.open("r", encoding="utf-8") as f:
    ingredients = json.load(f)["ingredients"]

recipe_ids = [r["id"] for r in recipes]
ingredient_ids = [i["id"] for i in ingredients]
valid_ids = set(ingredient_ids)

assert len(recipe_ids) == len(set(recipe_ids)), "Duplicate recipe IDs"
assert len(ingredient_ids) == len(set(ingredient_ids)), "Duplicate ingredient IDs"

normalized_count = 0
detailed_count = 0
instruction_count = 0
invalid_references = []
statuses = Counter()

for recipe in recipes:
    normalized = recipe.get("ingredients_normalized", [])
    detailed = recipe.get("ingredients_detailed", [])
    instructions = recipe.get("instructions", [])

    normalized_count += len(normalized)
    detailed_count += len(detailed)
    instruction_count += len(instructions)

    for item in normalized:
        statuses[item.get("status", "missing_status")] += 1

        ingredient_id = item.get("id")
        if ingredient_id and ingredient_id not in valid_ids:
            invalid_references.append(
                (recipe["id"], item.get("original"), ingredient_id)
            )

        for component in item.get("components", []):
            component_id = component.get("id")
            if component_id and component_id not in valid_ids:
                invalid_references.append(
                    (recipe["id"], component.get("original"), component_id)
                )

        for alternative in item.get("alternatives", []):
            alternative_id = alternative.get("id")
            if alternative_id and alternative_id not in valid_ids:
                invalid_references.append(
                    (recipe["id"], alternative.get("original"), alternative_id)
                )

print("=" * 65)
print("FULL PROJECT VALIDATION")
print("=" * 65)

print(f"Recipes: {len(recipes)}")
print(f"Unique recipe IDs: {len(set(recipe_ids))}")
print(f"Canonical ingredients: {len(ingredients)}")
print(f"Unique ingredient IDs: {len(set(ingredient_ids))}")
print(f"Normalized ingredient records: {normalized_count}")
print(f"Detailed ingredient records: {detailed_count}")
print(f"Instruction steps: {instruction_count}")

print("\nNormalization statuses:")
for status, count in sorted(statuses.items()):
    print(f"  {status}: {count}")

print(f"\nInvalid ingredient references: {len(invalid_references)}")

for reference in invalid_references:
    print("  ", reference)

assert not invalid_references, "Invalid ingredient references found!"

print("\nAll structural and reference checks passed.")
