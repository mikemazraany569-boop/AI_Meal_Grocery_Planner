
import json
import sys
from pathlib import Path
from collections import Counter


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

RECIPES_PATH = (
    PROJECT_ROOT
    / "data"
    / "recipes"
    / "lebanese_recipes_enriched.json"
)

INGREDIENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "ingredients"
    / "ingredients_multilingual.json"
)

sys.path.insert(0, str(PROJECT_ROOT))

from src.rag.recipe_document_builder import RecipeDocumentBuilder


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("INGREDIENT GROUP VALIDATION — READ ONLY")
print("=" * 70)

if not RECIPES_PATH.exists():
    raise FileNotFoundError(f"Recipes file not found: {RECIPES_PATH}")

if not INGREDIENTS_PATH.exists():
    raise FileNotFoundError(
        f"Ingredient dictionary not found: {INGREDIENTS_PATH}"
    )

with RECIPES_PATH.open("r", encoding="utf-8") as file:
    recipe_data = json.load(file)

if isinstance(recipe_data, dict):
    recipes = recipe_data.get("recipes", [])
elif isinstance(recipe_data, list):
    recipes = recipe_data
else:
    raise ValueError("Unexpected recipe JSON structure.")

print(f"\nRecipes loaded: {len(recipes)}")


# ============================================================
# BUILD DOCUMENTS IN MEMORY
# ============================================================

builder = RecipeDocumentBuilder(
    ingredients_path=INGREDIENTS_PATH
)

documents = builder.build_documents(recipes)

print(f"Documents built: {len(documents)}")


# ============================================================
# VALIDATION
# ============================================================

errors = []
warnings = []

total_groups = 0
total_required = 0
total_optional = 0

recipes_with_duplicates = 0
recipes_with_empty_groups = 0
recipes_with_group_mismatches = 0
recipes_with_classification_errors = 0
recipes_with_duplicate_ids = 0

target_recipe_ids = {
    "LB004",
    "LB006",
    "LB009",
    "LB011",
    "LB012",
    "LB015",
    "LB037",
    "LB038",
    "LB041",
    "LB049",
}

target_results = {}

for document in documents:

    metadata = document["metadata"]
    recipe_id = metadata.get("id", "UNKNOWN")

    ingredient_ids = metadata.get("ingredient_ids", [])
    groups = metadata.get("ingredient_groups", [])
    required_groups = metadata.get("required_ingredient_groups", [])
    optional_groups = metadata.get("optional_ingredient_groups", [])

    total_groups += len(groups)
    total_required += len(required_groups)
    total_optional += len(optional_groups)

    # --------------------------------------------------------
    # 1. Check duplicate ingredient IDs in ingredient_ids
    # --------------------------------------------------------

    duplicate_ids = [
        ingredient_id
        for ingredient_id, count in Counter(ingredient_ids).items()
        if count > 1
    ]

    if duplicate_ids:
        recipes_with_duplicate_ids += 1
        errors.append(
            f"{recipe_id}: duplicate ingredient_ids: {duplicate_ids}"
        )

    # --------------------------------------------------------
    # 2. Check empty groups
    # --------------------------------------------------------

    empty_groups = [
        index
        for index, group in enumerate(groups)
        if not group
    ]

    if empty_groups:
        recipes_with_empty_groups += 1
        errors.append(
            f"{recipe_id}: empty groups at indexes {empty_groups}"
        )

    # --------------------------------------------------------
    # 3. Check repeated IDs across groups
    # --------------------------------------------------------

    flattened_ids = [
        ingredient_id
        for group in groups
        for ingredient_id in group
    ]

    duplicate_group_ids = [
        ingredient_id
        for ingredient_id, count in Counter(flattened_ids).items()
        if count > 1
    ]

    if duplicate_group_ids:
        recipes_with_duplicates += 1
        errors.append(
            f"{recipe_id}: repeated IDs across groups: "
            f"{duplicate_group_ids}"
        )

    # --------------------------------------------------------
    # 4. Check ingredient_ids and group IDs consistency
    # --------------------------------------------------------

    ingredient_id_set = set(ingredient_ids)
    group_id_set = set(flattened_ids)

    missing_from_groups = ingredient_id_set - group_id_set
    missing_from_ingredient_ids = group_id_set - ingredient_id_set

    if missing_from_groups or missing_from_ingredient_ids:
        recipes_with_group_mismatches += 1

        errors.append(
            f"{recipe_id}: group IDs and ingredient IDs differ | "
            f"Missing from groups: {sorted(missing_from_groups)} | "
            f"Missing from ingredient_ids: "
            f"{sorted(missing_from_ingredient_ids)}"
        )

    # --------------------------------------------------------
    # 5. Check required/optional classification
    # --------------------------------------------------------

    required_ids = {
        ingredient_id
        for group in required_groups
        for ingredient_id in group
    }

    optional_ids = {
        ingredient_id
        for group in optional_groups
        for ingredient_id in group
    }

    overlap = required_ids.intersection(optional_ids)

    if overlap:
        recipes_with_classification_errors += 1
        errors.append(
            f"{recipe_id}: IDs classified as both required "
            f"and optional: {sorted(overlap)}"
        )

    classified_ids = required_ids.union(optional_ids)

    unclassified_ids = group_id_set - classified_ids
    unknown_classified_ids = classified_ids - group_id_set

    if unclassified_ids or unknown_classified_ids:
        recipes_with_classification_errors += 1

        errors.append(
            f"{recipe_id}: classification mismatch | "
            f"Unclassified: {sorted(unclassified_ids)} | "
            f"Unknown: {sorted(unknown_classified_ids)}"
        )

    # --------------------------------------------------------
    # 6. Check alternatives are not lost
    # --------------------------------------------------------

    original_recipe = metadata.get("recipe", {})

    normalized = original_recipe.get(
        "ingredients_normalized", []
    )

    original_alternative_ids = set()

    for item in normalized:
        if not isinstance(item, dict):
            continue

        for alternative in item.get("alternatives", []):
            if isinstance(alternative, dict):
                ingredient_id = alternative.get("id")
                if ingredient_id:
                    original_alternative_ids.add(ingredient_id)

    missing_alternatives = (
        original_alternative_ids - group_id_set
    )

    if missing_alternatives:
        errors.append(
            f"{recipe_id}: alternative IDs missing from groups: "
            f"{sorted(missing_alternatives)}"
        )

    # --------------------------------------------------------
    # 7. Save target recipe results
    # --------------------------------------------------------

    if recipe_id in target_recipe_ids:
        target_results[recipe_id] = {
            "name": metadata.get("name_en"),
            "groups": groups,
            "required": required_groups,
            "optional": optional_groups,
            "ingredient_ids": ingredient_ids,
        }


# ============================================================
# TARGET RECIPE REPORT
# ============================================================

print("\n" + "=" * 70)
print("TARGET RECIPE RESULTS")
print("=" * 70)

for recipe_id in sorted(target_recipe_ids):

    result = target_results.get(recipe_id)

    if result is None:
        print(f"\n{recipe_id}: NOT FOUND")
        warnings.append(f"{recipe_id}: target recipe not found")
        continue

    print(f"\n{recipe_id} — {result['name']}")
    print(f"Total groups: {len(result['groups'])}")
    print(f"Required groups: {len(result['required'])}")
    print(f"Optional groups: {len(result['optional'])}")
    print(f"Ingredient IDs: {len(result['ingredient_ids'])}")
    print(f"Groups: {result['groups']}")

    if recipe_id == "LB049":
        onion_groups = [
            group
            for group in result["required"]
            if "ING002" in group
        ]

        optional_onion_groups = [
            group
            for group in result["optional"]
            if "ING002" in group
        ]

        print(f"LB049 onion required: {bool(onion_groups)}")
        print(f"LB049 onion optional: {bool(optional_onion_groups)}")


# ============================================================
# VALIDATION SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

print(f"Recipes tested: {len(documents)}")
print(f"Total ingredient groups: {total_groups}")
print(f"Required groups: {total_required}")
print(f"Optional groups: {total_optional}")

print(f"\nRecipes with repeated group IDs: {recipes_with_duplicates}")
print(f"Recipes with empty groups: {recipes_with_empty_groups}")
print(f"Recipes with ID mismatches: {recipes_with_group_mismatches}")
print(
    "Recipes with duplicate ingredient_ids: "
    f"{recipes_with_duplicate_ids}"
)
print(
    "Recipes with classification errors: "
    f"{recipes_with_classification_errors}"
)

print(f"\nValidation errors: {len(errors)}")
print(f"Warnings: {len(warnings)}")

if errors:
    print("\nERRORS:")
    for error in errors:
        print(f"- {error}")

if warnings:
    print("\nWARNINGS:")
    for warning in warnings:
        print(f"- {warning}")

if not errors:
    print("\nALL VALIDATION CHECKS PASSED.")

print("\nNo files modified.")
print("=" * 70)
