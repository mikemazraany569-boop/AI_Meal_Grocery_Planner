import json
import shutil
from datetime import datetime
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent

RECIPES_FILE = (
    BASE_DIR / "data" / "recipes" / "lebanese_recipes_enriched.json"
)

INGREDIENTS_FILE = (
    BASE_DIR / "data" / "ingredients" / "ingredients_multilingual.json"
)

PEPPER_ID = "ING015"
CORIANDER_ID = "ING030"

DIRECT_MAPPINGS = [
    ("LB002", 3, "pepper", PEPPER_ID, "black pepper"),
    ("LB024", 5, "pepper", PEPPER_ID, "black pepper"),
    ("LB025", 5, "pepper", PEPPER_ID, "black pepper"),
    ("LB028", 7, "pepper", PEPPER_ID, "black pepper"),
    ("LB039", 7, "pepper", PEPPER_ID, "black pepper"),
    ("LB029", 2, "coriander", CORIANDER_ID, "fresh coriander"),
    ("LB030", 3, "coriander", CORIANDER_ID, "fresh coriander"),
]

COMPOSITE_MAPPING = {
    "recipe_id": "LB007",
    "index": 11,
    "parent_original": "salt and pepper",
    "component_original": "pepper",
    "ingredient_id": PEPPER_ID,
    "canonical_name": "black pepper",
}


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


def get_recipe(recipes, recipe_id):
    matches = [
        recipe for recipe in recipes
        if recipe.get("id") == recipe_id
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one recipe {recipe_id}; "
            f"found {len(matches)}."
        )

    return matches[0]


def check_unique_ingredient_ids(ingredients):
    ids = [item.get("id") for item in ingredients]

    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate ingredient IDs detected.")

    if not all(ids):
        raise ValueError("An ingredient has a missing ID.")


def find_ingredient(ingredients, ingredient_id):
    matches = [
        item for item in ingredients
        if item.get("id") == ingredient_id
    ]

    if len(matches) != 1:
        raise ValueError(
            f"Expected exactly one {ingredient_id}; "
            f"found {len(matches)}."
        )

    return matches[0]


def count_alias(ingredients, alias):
    alias = alias.casefold()

    return sum(
        1
        for ingredient in ingredients
        for aliases in ingredient.get("names", {}).values()
        if isinstance(aliases, list)
        for existing in aliases
        if isinstance(existing, str)
        and existing.casefold() == alias
    )


def check_alias_collision(ingredients, alias, target_id):
    alias = alias.casefold()

    for ingredient in ingredients:
        names = ingredient.get("names", {})

        for aliases in names.values():
            if not isinstance(aliases, list):
                continue

            for existing in aliases:
                if not isinstance(existing, str):
                    continue

                if existing.casefold() == alias:
                    if ingredient.get("id") != target_id:
                        raise ValueError(
                            f"Alias collision: '{alias}' belongs to "
                            f"{ingredient.get('id')}, not {target_id}."
                        )


def validate_target_record(recipe, index, expected_original):
    normalized = recipe.get("ingredients_normalized", [])
    detailed = recipe.get("ingredients_detailed", [])

    if index >= len(normalized) or index >= len(detailed):
        raise ValueError(
            f"Index {index} is outside the ingredient arrays "
            f"for {recipe.get('id')}."
        )

    record = normalized[index]
    detail = detailed[index]

    if record.get("original") != expected_original:
        raise ValueError(
            f"Unexpected normalized ingredient in {recipe.get('id')} "
            f"at index {index}: {record.get('original')!r}"
        )

    detail_name = detail.get("name")

    if not isinstance(detail_name, str):
        raise ValueError(
            f"Missing or invalid detailed ingredient name "
            f"in {recipe.get('id')} at index {index}."
        )

    if detail_name.casefold() != expected_original.casefold():
        raise ValueError(
            f"Unexpected detailed ingredient in {recipe.get('id')} "
            f"at index {index}: {detail_name!r}"
        )

    if record.get("status") != "needs_review":
        raise ValueError(
            f"{recipe.get('id')} index {index} is not needs_review. "
            "Refusing to overwrite an existing mapping."
        )

    return record, detail


def validate_updated_files(recipes_data, ingredients_data):
    recipes = recipes_data["recipes"]
    ingredients = ingredients_data["ingredients"]

    check_unique_ingredient_ids(ingredients)

    check_recipe_lookup = {}

    for recipe in recipes:
        recipe_id = recipe.get("id")

        if recipe_id in check_recipe_lookup:
            raise ValueError(f"Duplicate recipe ID: {recipe_id}")

        check_recipe_lookup[recipe_id] = recipe

    for recipe_id, index, original, ingredient_id, canonical in DIRECT_MAPPINGS:
        if recipe_id not in check_recipe_lookup:
            raise ValueError(f"Missing recipe: {recipe_id}")

        recipe = check_recipe_lookup[recipe_id]
        record = recipe["ingredients_normalized"][index]
        detail = recipe["ingredients_detailed"][index]

        assert record["original"] == original
        assert record["id"] == ingredient_id
        assert record["canonical_name"] == canonical
        assert record["status"] == "matched"
        assert detail["ingredient_id"] == ingredient_id
        assert detail["canonical_name"] == canonical

    composite = check_recipe_lookup["LB007"][
        "ingredients_normalized"
    ][11]

    assert composite["original"] == "salt and pepper"

    pepper_components = [
        component
        for component in composite.get("components", [])
        if component.get("original") == "pepper"
    ]

    assert len(pepper_components) == 1

    pepper_component = pepper_components[0]

    assert pepper_component["id"] == PEPPER_ID
    assert pepper_component["canonical_name"] == "black pepper"
    assert pepper_component["status"] == "matched"

    # The generic coriander alias must exist exactly once.
    assert count_alias(ingredients, "coriander") == 1

    coriander = find_ingredient(ingredients, CORIANDER_ID)

    assert any(
        isinstance(alias, str)
        and alias.casefold() == "coriander"
        for alias in coriander.get("names", {}).get("en", [])
    )


def main():
    print("=" * 75)
    print("BATCH 5 — SAFE INGREDIENT NORMALIZATION")
    print("=" * 75)

    if not RECIPES_FILE.exists():
        raise FileNotFoundError(RECIPES_FILE)

    if not INGREDIENTS_FILE.exists():
        raise FileNotFoundError(INGREDIENTS_FILE)

    recipes_data = load_json(RECIPES_FILE)
    ingredients_data = load_json(INGREDIENTS_FILE)

    recipes = recipes_data["recipes"]
    ingredients = ingredients_data["ingredients"]

    check_unique_ingredient_ids(ingredients)

    pepper = find_ingredient(ingredients, PEPPER_ID)
    coriander = find_ingredient(ingredients, CORIANDER_ID)

    print("\nCanonical ingredients verified:")
    print(f"{PEPPER_ID}: {pepper['names'].get('en', [])}")
    print(f"{CORIANDER_ID}: {coriander['names'].get('en', [])}")

    check_alias_collision(
        ingredients,
        "coriander",
        CORIANDER_ID
    )

    # Preflight all direct mappings before changing anything.
    targets = []

    for recipe_id, index, original, ingredient_id, canonical in DIRECT_MAPPINGS:
        recipe = get_recipe(recipes, recipe_id)

        record, detail = validate_target_record(
            recipe,
            index,
            original
        )

        targets.append((
            recipe,
            record,
            detail,
            ingredient_id,
            canonical
        ))

    # Preflight the composite pepper component.
    composite_recipe = get_recipe(
        recipes,
        COMPOSITE_MAPPING["recipe_id"]
    )

    composite_index = COMPOSITE_MAPPING["index"]
    composite_normalized = composite_recipe["ingredients_normalized"]

    if composite_index >= len(composite_normalized):
        raise ValueError("LB007 composite index is outside the array.")

    composite_record = composite_normalized[composite_index]

    if composite_record.get("original") != COMPOSITE_MAPPING["parent_original"]:
        raise ValueError("Unexpected LB007 composite ingredient.")

    if composite_record.get("status") != "needs_review":
        raise ValueError("LB007 composite is not needs_review.")

    components = composite_record.get("components", [])

    component_matches = [
        component
        for component in components
        if component.get("original") ==
        COMPOSITE_MAPPING["component_original"]
    ]

    if len(component_matches) != 1:
        raise ValueError(
            "Expected exactly one pepper component in LB007."
        )

    pepper_component = component_matches[0]

    if pepper_component.get("id") or pepper_component.get("ingredient_id"):
        raise ValueError(
            "LB007 pepper component already has a mapping."
        )

    if pepper_component.get("status") != "needs_review":
        raise ValueError(
            "LB007 pepper component is not needs_review."
        )

    # Prepare changes in memory.
    for recipe, record, detail, ingredient_id, canonical in targets:
        record["id"] = ingredient_id
        record["canonical_name"] = canonical
        record["status"] = "matched"

        if ingredient_id == PEPPER_ID:
            record["mapping_note"] = (
                "Contextual mapping: original source says "
                "'pepper'; interpreted as black pepper from "
                "the savory recipe context. This is an inference."
            )
        else:
            record["mapping_note"] = (
                "Mapped to fresh coriander (ING030) "
                "according to the approved normalization decision."
            )

        detail["ingredient_id"] = ingredient_id
        detail["canonical_name"] = canonical

    # Add the generic coriander alias if needed.
    english_names = (
        coriander.setdefault("names", {}).setdefault("en", [])
    )

    if not any(
        isinstance(name, str)
        and name.casefold() == "coriander"
        for name in english_names
    ):
        english_names.append("coriander")
        print("\nAdded English alias 'coriander' to ING030.")
    else:
        print("\nEnglish alias 'coriander' already exists in ING030.")

    # Resolve only the pepper component inside LB007.
    pepper_component["id"] = PEPPER_ID
    pepper_component["canonical_name"] = "black pepper"
    pepper_component["status"] = "matched"
    pepper_component["mapping_note"] = (
        "Contextual inference: generic pepper interpreted "
        "as black pepper."
    )

    # Validate all changes in memory before creating backups.
    validate_updated_files(recipes_data, ingredients_data)

    # Create unique backups.
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    recipe_backup = RECIPES_FILE.with_name(
        f"{RECIPES_FILE.stem}.backup_batch5_{timestamp}"
        f"{RECIPES_FILE.suffix}"
    )

    ingredient_backup = INGREDIENTS_FILE.with_name(
        f"{INGREDIENTS_FILE.stem}.backup_batch5_{timestamp}"
        f"{INGREDIENTS_FILE.suffix}"
    )

    if recipe_backup.exists() or ingredient_backup.exists():
        raise FileExistsError(
            "Backup already exists. Refusing to overwrite."
        )

    shutil.copy2(RECIPES_FILE, recipe_backup)
    shutil.copy2(INGREDIENTS_FILE, ingredient_backup)

    # Temporary files and rollback staging files.
    recipe_temp = RECIPES_FILE.with_name(
        RECIPES_FILE.name + ".batch5.tmp"
    )

    ingredient_temp = INGREDIENTS_FILE.with_name(
        INGREDIENTS_FILE.name + ".batch5.tmp"
    )

    recipe_restore_temp = RECIPES_FILE.with_name(
        RECIPES_FILE.name + ".batch5.restore"
    )

    ingredient_restore_temp = INGREDIENTS_FILE.with_name(
        INGREDIENTS_FILE.name + ".batch5.restore"
    )

    temporary_paths = [
        recipe_temp,
        ingredient_temp,
        recipe_restore_temp,
        ingredient_restore_temp,
    ]

    for path in temporary_paths:
        if path.exists():
            raise FileExistsError(
                f"Temporary file already exists: {path}. "
                "Inspect it before running again."
            )

    try:
        # Write temporary files.
        save_json(recipe_temp, recipes_data)
        save_json(ingredient_temp, ingredients_data)

        # Re-read and validate the temporary JSON files.
        check_recipes = load_json(recipe_temp)
        check_ingredients = load_json(ingredient_temp)

        validate_updated_files(
            check_recipes,
            check_ingredients
        )

        # Prepare rollback copies before replacing either original.
        shutil.copy2(recipe_backup, recipe_restore_temp)
        shutil.copy2(ingredient_backup, ingredient_restore_temp)

        try:
            os.replace(recipe_temp, RECIPES_FILE)
            os.replace(ingredient_temp, INGREDIENTS_FILE)

        except Exception as replacement_error:
            print("\nERROR during file replacement.")
            print("Attempting to restore both original files...")

            try:
                if recipe_restore_temp.exists():
                    os.replace(recipe_restore_temp, RECIPES_FILE)

                if ingredient_restore_temp.exists():
                    os.replace(ingredient_restore_temp, INGREDIENTS_FILE)

            except Exception as rollback_error:
                raise RuntimeError(
                    "CRITICAL: automatic rollback was not fully "
                    "successful. Original backup files are preserved. "
                    f"Recipe backup: {recipe_backup}. "
                    f"Ingredient backup: {ingredient_backup}. "
                    f"Rollback error: {rollback_error}"
                ) from replacement_error

            raise RuntimeError(
                "Batch 5 failed. Original files restored from backups."
            ) from replacement_error

        # Verify the files after replacement.
        final_recipes = load_json(RECIPES_FILE)
        final_ingredients = load_json(INGREDIENTS_FILE)

        validate_updated_files(
            final_recipes,
            final_ingredients
        )

    finally:
        for path in temporary_paths:
            if path.exists():
                path.unlink()

    print("\n" + "=" * 75)
    print("BATCH 5 COMPLETED")
    print("=" * 75)

    print(f"Direct mappings completed: {len(targets)}")
    print("Composite components resolved: 1")
    print(f"Ingredient dictionary total: {len(ingredients)}")
    print(
        "Generic coriander alias count:",
        count_alias(ingredients, "coriander")
    )

    print("\nUpdated records:")

    for recipe, record, detail, ingredient_id, canonical in targets:
        print(
            f"{recipe['id']} | {record['original']} "
            f"-> {canonical} ({ingredient_id})"
        )

    print("\nLB007:")
    print("salt -> ING014 (unchanged)")
    print("pepper -> ING015 (new component mapping)")
    print("Parent 'salt and pepper' remains needs_review.")

    print("\nBackups created:")
    print(recipe_backup)
    print(ingredient_backup)

    print("\nNo other recipe mappings were changed.")
    print("Stock and broth alternatives remain unresolved.")
    print("Long green peppers and generic meat remain unresolved.")


if __name__ == "__main__":
    main()
