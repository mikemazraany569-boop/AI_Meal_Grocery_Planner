
import json
from pathlib import Path
from collections import Counter

RECIPE_PATH = Path("data/recipes/lebanese_recipes_enriched.json")
INGREDIENT_PATH = Path("data/ingredients/ingredients_multilingual.json")

with open(RECIPE_PATH, "r", encoding="utf-8") as f:
    recipes = json.load(f)["recipes"]

with open(INGREDIENT_PATH, "r", encoding="utf-8") as f:
    ingredients = json.load(f)["ingredients"]

valid_ingredient_ids = {item["id"] for item in ingredients}

recipe_ids = [r["id"] for r in recipes]
ingredient_ids = [i["id"] for i in ingredients]

errors = []
warnings = []

print("=" * 70)
print("FULL LEBANESE RECIPE KNOWLEDGE BASE VALIDATION")
print("=" * 70)

# 1. Counts and unique IDs
print("\n1. COUNTS AND UNIQUE IDs")

print(f"Recipes: {len(recipes)}")
print(f"Unique recipe IDs: {len(set(recipe_ids))}")
print(f"Canonical ingredients: {len(ingredients)}")
print(f"Unique ingredient IDs: {len(set(ingredient_ids))}")

if len(recipe_ids) != len(set(recipe_ids)):
    errors.append("Duplicate recipe IDs found.")

if len(ingredient_ids) != len(set(ingredient_ids)):
    errors.append("Duplicate ingredient IDs found.")

# 2. Recipe structure
print("\n2. RECIPE STRUCTURE")

total_detailed = 0
total_normalized = 0
total_instructions = 0
total_references = 0

for recipe in recipes:
    rid = recipe["id"]

    detailed = recipe.get("ingredients_detailed", [])
    normalized = recipe.get("ingredients_normalized", [])
    instructions = recipe.get("instructions", [])

    total_detailed += len(detailed)
    total_normalized += len(normalized)
    total_instructions += len(instructions)

    if not detailed:
        errors.append(f"{rid}: no detailed ingredients.")

    if not normalized:
        errors.append(f"{rid}: no normalized ingredients.")

    if len(detailed) != len(normalized):
        errors.append(
            f"{rid}: detailed/normalized count mismatch "
            f"({len(detailed)} vs {len(normalized)})."
        )

    if not instructions:
        errors.append(f"{rid}: missing instructions.")

    for step in instructions:
        if not isinstance(step, dict) or not step.get("text_en"):
            errors.append(f"{rid}: invalid instruction structure.")

    # Check detailed ingredient references.
    for item in detailed:
        ingredient_id = item.get("ingredient_id")

        if ingredient_id is not None:
            total_references += 1
            if ingredient_id not in valid_ingredient_ids:
                errors.append(
                    f"{rid}: invalid detailed ingredient ID {ingredient_id}."
                )

    # Check normalized components and alternatives.
    for item in normalized:
        for field in ("components", "alternatives"):
            for component in item.get(field, []):
                component_id = component.get("id")

                if component_id is not None:
                    total_references += 1
                    if component_id not in valid_ingredient_ids:
                        errors.append(
                            f"{rid}: invalid {field} ID {component_id}."
                        )

print(f"Detailed ingredient records: {total_detailed}")
print(f"Normalized ingredient records: {total_normalized}")
print(f"Instruction steps: {total_instructions}")
print(f"Validated ingredient references: {total_references}")

# 3. Normalization status summary
print("\n3. NORMALIZATION STATUS")

status_counts = Counter(
    item.get("status", "missing")
    for recipe in recipes
    for item in recipe.get("ingredients_normalized", [])
)

for status, count in sorted(status_counts.items()):
    print(f"{status}: {count}")

# 4. Verification status summary
print("\n4. RECIPE VERIFICATION STATUS")

verification_counts = Counter(
    recipe.get("verification_status", "missing")
    for recipe in recipes
)

for status, count in sorted(verification_counts.items()):
    print(f"{status}: {count}")

# 5. Batch 4-specific checks
print("\n5. BATCH 4 CHECKS")

batch4 = [
    r for r in recipes
    if r["id"] in {f"LB{i:03d}" for i in range(46, 51)}
]

for recipe in sorted(batch4, key=lambda r: r["id"]):
    rid = recipe["id"]

    unresolved = [
        choice
        for item in recipe["ingredients_normalized"]
        for choice in item.get("alternatives", [])
        if choice.get("id") is None
    ]

    print(
        f"{rid}: {len(recipe['ingredients_detailed'])} ingredients | "
        f"{len(recipe['instructions'])} steps | "
        f"{len(unresolved)} unresolved alternatives"
    )

spinach_recipe = next(
    (r for r in batch4 if r["id"] == "LB048"),
    None
)

if spinach_recipe:
    spinach = next(
        (
            item for item in spinach_recipe["ingredients_detailed"]
            if item["name"] == "fresh spinach or frozen leaf spinach"
        ),
        None
    )

    if not spinach or not spinach.get("source_quantity_notes"):
        errors.append(
            "LB048: spinach source quantity notes are missing."
        )
    else:
        print("LB048: fresh/frozen spinach source quantities preserved.")

if len(batch4) != 5:
    errors.append(f"Expected 5 Batch 4 recipes, found {len(batch4)}.")

# 6. Final result
print("\n" + "=" * 70)
print("VALIDATION RESULT")
print("=" * 70)

if errors:
    print(f"FAILED: {len(errors)} error(s)")
    for error in errors:
        print(f"ERROR: {error}")
else:
    print("ALL STRUCTURAL CHECKS PASSED")

if warnings:
    print("\nWARNINGS:")
    for warning in warnings:
        print(warning)

print("\nNote: needs_review records are not structural errors.")
