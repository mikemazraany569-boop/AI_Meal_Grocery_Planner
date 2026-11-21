import json
import shutil
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RECIPES_FILE = (
    BASE_DIR / "data" / "recipes" / "lebanese_recipes_enriched.json"
)

INGREDIENTS_FILE = (
    BASE_DIR / "data" / "ingredients" / "ingredients_multilingual.json"
)

RECIPE_ID = "LB002"
INDEX = 0

LAMB_ID = "ING023"
ONION_ID = "ING002"

SOURCE_ORIGINAL = "Lamb ground onions"

INTERPRETATION_NOTE = (
    "Interpretation: the original source phrase 'Lamb ground onions' "
    "is split into ground lamb and onion. This is an inferred "
    "decomposition, not a verified transcription of two separate "
    "source ingredient entries."
)


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            ensure_ascii=False,
            indent=2
        )
        file.write("\n")


def get_unique_recipe(recipes, recipe_id):
    matches = [
        recipe for recipe in recipes
        if recipe.get("id") == recipe_id
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {recipe_id}; found {len(matches)}."
        )

    return matches[0]


def get_unique_ingredient(ingredients, ingredient_id):
    matches = [
        item for item in ingredients
        if item.get("id") == ingredient_id
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {ingredient_id}; found {len(matches)}."
        )

    return matches[0]


def validate_unique_ids(ingredients):
    ids = [item.get("id") for item in ingredients]

    if not all(ids):
        raise ValueError("An ingredient has a missing ID.")

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate canonical ingredient IDs found.")


def validate_component(component, original, ingredient_id, canonical):
    assert component.get("original") == original
    assert component.get("id") == ingredient_id
    assert component.get("canonical_name") == canonical
    assert component.get("status") == "matched"


def validate_project(recipes_data, ingredients_data):
    recipes = recipes_data["recipes"]
    ingredients = ingredients_data["ingredients"]

    validate_unique_ids(ingredients)

    recipe = get_unique_recipe(recipes, RECIPE_ID)

    normalized = recipe["ingredients_normalized"]
    detailed = recipe["ingredients_detailed"]

    if len(normalized) != len(detailed):
        raise ValueError(
            "LB002 normalized and detailed ingredient counts differ."
        )

    parent = normalized[INDEX]

    if parent.get("original") != SOURCE_ORIGINAL:
        raise ValueError("LB002 source wording changed unexpectedly.")

    if parent.get("status") != "needs_review":
        raise ValueError("LB002 composite parent status is incorrect.")

    if parent.get("id") or parent.get("ingredient_id"):
        raise ValueError("Composite parent must not have a direct ID.")

    components = parent.get("components", [])

    if len(components) != 2:
        raise ValueError("Expected exactly two LB002 components.")

    ground_lamb = [
        c for c in components
        if c.get("original") == "ground lamb"
    ]

    onion = [
        c for c in components
        if c.get("original") == "onion"
    ]

    if len(ground_lamb) != 1 or len(onion) != 1:
        raise ValueError("LB002 component names are incorrect.")

    validate_component(
        ground_lamb[0], "ground lamb", LAMB_ID, "lamb"
    )

    validate_component(
        onion[0], "onion", ONION_ID, "onion"
    )

    assert parent.get("mapping_note") == INTERPRETATION_NOTE

    # The detailed source record remains intact and unmapped
    # because it represents the original composite phrase.
    detail = detailed[INDEX]

    assert detail.get("name") == SOURCE_ORIGINAL
    assert detail.get("quantity") is None
    assert detail.get("unit") is None
    assert detail.get("ingredient_id") is None
    assert detail.get("canonical_name") is None

    # Validate all top-level, component, and alternative references.
    valid_ids = {item["id"] for item in ingredients}

    for current_recipe in recipes:
        for record in current_recipe.get(
            "ingredients_normalized", []
        ):
            ingredient_id = record.get("id")

            if ingredient_id and ingredient_id not in valid_ids:
                raise ValueError(
                    f"Invalid reference in {current_recipe['id']}: "
                    f"{ingredient_id}"
                )

            for component in record.get("components", []):
                component_id = component.get("id")

                if component_id and component_id not in valid_ids:
                    raise ValueError(
                        f"Invalid component reference in "
                        f"{current_recipe['id']}: {component_id}"
                    )

            for alternative in record.get("alternatives", []):
                alternative_id = alternative.get("id")

                if alternative_id and alternative_id not in valid_ids:
                    raise ValueError(
                        f"Invalid alternative reference in "
                        f"{current_recipe['id']}: {alternative_id}"
                    )


def is_already_applied(recipes_data):
    recipe = get_unique_recipe(
        recipes_data["recipes"], RECIPE_ID
    )

    parent = recipe["ingredients_normalized"][INDEX]
    components = parent.get("components", [])

    return (
        parent.get("original") == SOURCE_ORIGINAL
        and parent.get("status") == "needs_review"
        and len(components) == 2
        and any(
            c.get("original") == "ground lamb"
            and c.get("id") == LAMB_ID
            for c in components
        )
        and any(
            c.get("original") == "onion"
            and c.get("id") == ONION_ID
            for c in components
        )
    )


def main():
    print("=" * 70)
    print("BATCH 6 — LB002 COMPOSITE INGREDIENT NORMALIZATION")
    print("=" * 70)

    if not RECIPES_FILE.exists():
        raise FileNotFoundError(RECIPES_FILE)

    if not INGREDIENTS_FILE.exists():
        raise FileNotFoundError(INGREDIENTS_FILE)

    recipes_data = load_json(RECIPES_FILE)
    ingredients_data = load_json(INGREDIENTS_FILE)

    recipes = recipes_data["recipes"]
    ingredients = ingredients_data["ingredients"]

    validate_unique_ids(ingredients)

    lamb = get_unique_ingredient(ingredients, LAMB_ID)
    onion = get_unique_ingredient(ingredients, ONION_ID)

    print("\nCanonical ingredients verified:")
    print(f"{LAMB_ID}: {lamb.get('names', {}).get('en', [])}")
    print(f"{ONION_ID}: {onion.get('names', {}).get('en', [])}")

    recipe = get_unique_recipe(recipes, RECIPE_ID)

    if INDEX >= len(recipe.get("ingredients_normalized", [])):
        raise ValueError("LB002 ingredient index not found.")

    if INDEX >= len(recipe.get("ingredients_detailed", [])):
        raise ValueError("LB002 detailed ingredient index not found.")

    # Avoid applying the same update twice.
    if is_already_applied(recipes_data):
        validate_project(recipes_data, ingredients_data)

        print("\nBatch 6 is already applied and validated.")
        print("No files were modified.")
        return

    parent = recipe["ingredients_normalized"][INDEX]
    detail = recipe["ingredients_detailed"][INDEX]

    # Strict preflight checks.
    if parent.get("original") != SOURCE_ORIGINAL:
        raise ValueError("Unexpected LB002 normalized source phrase.")

    if detail.get("name") != SOURCE_ORIGINAL:
        raise ValueError("Unexpected LB002 detailed source phrase.")

    if parent.get("status") != "needs_review":
        raise ValueError("LB002 is not needs_review.")

    if parent.get("id") or parent.get("ingredient_id"):
        raise ValueError("LB002 already has a direct ingredient mapping.")

    if parent.get("components") or parent.get("alternatives"):
        raise ValueError(
            "LB002 already has components or alternatives. "
            "Inspect manually before proceeding."
        )

    if detail.get("ingredient_id") or detail.get("canonical_name"):
        raise ValueError(
            "Detailed LB002 record already has a mapping."
        )

    if detail.get("quantity") is not None or detail.get("unit") is not None:
        raise ValueError(
            "Unexpected LB002 quantity or unit. "
            "Refusing to modify this record."
        )

    # Preserve the original source phrase and create two components.
    parent["components"] = [
        {
            "original": "ground lamb",
            "canonical_name": "lamb",
            "status": "matched",
            "id": LAMB_ID,
            "mapping_note": INTERPRETATION_NOTE
        },
        {
            "original": "onion",
            "canonical_name": "onion",
            "status": "matched",
            "id": ONION_ID,
            "mapping_note": INTERPRETATION_NOTE
        }
    ]

    # Parent remains needs_review because it is a composite.
    parent["status"] = "needs_review"
    parent["mapping_note"] = INTERPRETATION_NOTE

    # Do not alter the detailed source record or its quantities.

    # Validate the complete updated data in memory.
    validate_project(recipes_data, ingredients_data)

    print("\nIn-memory validation passed.")

    # Create timestamped backups.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    recipe_backup = RECIPES_FILE.with_name(
        f"{RECIPES_FILE.stem}.backup_batch6_{timestamp}"
        f"{RECIPES_FILE.suffix}"
    )

    ingredient_backup = INGREDIENTS_FILE.with_name(
        f"{INGREDIENTS_FILE.stem}.backup_batch6_{timestamp}"
        f"{INGREDIENTS_FILE.suffix}"
    )

    if recipe_backup.exists() or ingredient_backup.exists():
        raise FileExistsError(
            "Backup already exists. Refusing to overwrite."
        )

    recipe_temp = RECIPES_FILE.with_name(
        RECIPES_FILE.name + ".batch6.tmp"
    )

    ingredient_temp = INGREDIENTS_FILE.with_name(
        INGREDIENTS_FILE.name + ".batch6.tmp"
    )

    recipe_restore = RECIPES_FILE.with_name(
        RECIPES_FILE.name + ".batch6.restore"
    )

    ingredient_restore = INGREDIENTS_FILE.with_name(
        INGREDIENTS_FILE.name + ".batch6.restore"
    )

    temporary_paths = [
        recipe_temp,
        ingredient_temp,
        recipe_restore,
        ingredient_restore
    ]

    for path in temporary_paths:
        if path.exists():
            raise FileExistsError(
                f"Temporary file exists: {path}. "
                "Inspect it before running."
            )

    shutil.copy2(RECIPES_FILE, recipe_backup)
    shutil.copy2(INGREDIENTS_FILE, ingredient_backup)

    try:
        # Write and validate temporary JSON files.
        save_json(recipe_temp, recipes_data)
        save_json(ingredient_temp, ingredients_data)

        check_recipes = load_json(recipe_temp)
        check_ingredients = load_json(ingredient_temp)

        validate_project(check_recipes, check_ingredients)

        print("Temporary-file validation passed.")

        # Prepare rollback copies before replacing originals.
        shutil.copy2(recipe_backup, recipe_restore)
        shutil.copy2(ingredient_backup, ingredient_restore)

        try:
            os.replace(recipe_temp, RECIPES_FILE)
            os.replace(ingredient_temp, INGREDIENTS_FILE)

        except Exception as replacement_error:
            print("\nReplacement failed. Restoring backups...")

            try:
                os.replace(recipe_restore, RECIPES_FILE)
                os.replace(ingredient_restore, INGREDIENTS_FILE)

            except Exception as rollback_error:
                raise RuntimeError(
                    "CRITICAL: rollback was not fully successful. "
                    "Original backups have been preserved:\n"
                    f"{recipe_backup}\n{ingredient_backup}\n"
                    f"Rollback error: {rollback_error}"
                ) from replacement_error

            raise RuntimeError(
                "Batch 6 failed. Original files restored."
            ) from replacement_error

        # Validate the actual files after replacement.
        final_recipes = load_json(RECIPES_FILE)
        final_ingredients = load_json(INGREDIENTS_FILE)

        validate_project(final_recipes, final_ingredients)

        print("Final on-disk validation passed.")

    finally:
        for path in temporary_paths:
            if path.exists():
                path.unlink()

    print("\n" + "=" * 70)
    print("BATCH 6 COMPLETED SUCCESSFULLY")
    print("=" * 70)

    print("Recipe updated: LB002 - Batata mahchi")
    print("Original phrase: Lamb ground onions")
    print(f"Component 1: ground lamb -> {LAMB_ID}")
    print(f"Component 2: onion -> {ONION_ID}")
    print("Parent status: needs_review (composite)")
    print("Detailed source record: preserved")
    print("Quantity and unit: preserved (both null)")
    print("\nNo other recipes or ingredients were modified.")

    print("\nBackups:")
    print(recipe_backup)
    print(ingredient_backup)


if __name__ == "__main__":
    main()
