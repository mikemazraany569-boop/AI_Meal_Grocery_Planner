
import json
import shutil
import os
import tempfile
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).resolve().parent

RECIPE_FILE = BASE / "data/recipes/lebanese_recipes_enriched.json"
INGREDIENT_FILE = BASE / "data/ingredients/ingredients_multilingual.json"

RECIPE_ID = "LB041"
INDEX = 8
INGREDIENT_ID = "ING075"
CANONICAL_NAME = "green bell pepper"

NOTE = (
    "Inference: the source specifies 'long green peppers'. "
    "Mapped to ING075 (green bell pepper) as an approximation. "
    "The exact pepper variety is not verified by the source."
)

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def save_json_temp(data, original_path):
    fd, temp_name = tempfile.mkstemp(
        prefix=original_path.stem + "_",
        suffix=".tmp",
        dir=original_path.parent
    )
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return Path(temp_name)

def validate(data, ingredients):
    recipes = data["recipes"]
    ingredient_records = ingredients["ingredients"]

    ids = [
        item["id"] for item in ingredient_records
    ]

    assert ids.count(INGREDIENT_ID) == 1, (
        "ING075 must exist exactly once."
    )

    recipe_matches = [
        r for r in recipes if r.get("id") == RECIPE_ID
    ]
    assert len(recipe_matches) == 1, "LB041 must exist exactly once."

    recipe = recipe_matches[0]
    detailed = recipe["ingredients_detailed"]
    normalized = recipe["ingredients_normalized"]

    assert len(detailed) == len(normalized), (
        "Ingredient arrays have different lengths."
    )

    detail = detailed[INDEX]
    norm = normalized[INDEX]

    assert detail.get("name") == "long green peppers"
    assert norm.get("original") == "long green peppers"
    assert detail.get("ingredient_id") == INGREDIENT_ID
    assert detail.get("canonical_name") == CANONICAL_NAME
    assert norm.get("id") == INGREDIENT_ID
    assert norm.get("canonical_name") == CANONICAL_NAME
    assert norm.get("status") == "matched"
    assert norm.get("mapping_note") == NOTE

    valid_ids = set(ids)

    for recipe in recipes:
        for record in recipe.get("ingredients_detailed", []):
            ref = record.get("ingredient_id")
            assert ref is None or ref in valid_ids, (
                f"Invalid detailed reference: {ref}"
            )

        for record in recipe.get("ingredients_normalized", []):
            ref = record.get("id")
            assert ref is None or ref in valid_ids, (
                f"Invalid normalized reference: {ref}"
            )

            for component in record.get("components", []):
                ref = component.get("id")
                assert ref is None or ref in valid_ids

            for alternative in record.get("alternatives", []):
                ref = alternative.get("id")
                assert ref is None or ref in valid_ids

    return True

def main():
    if not RECIPE_FILE.exists() or not INGREDIENT_FILE.exists():
        raise FileNotFoundError("A required project JSON file is missing.")

    recipes_data = load_json(RECIPE_FILE)
    ingredients_data = load_json(INGREDIENT_FILE)

    recipe_matches = [
        r for r in recipes_data["recipes"]
        if r.get("id") == RECIPE_ID
    ]
    assert len(recipe_matches) == 1

    recipe = recipe_matches[0]
    detail = recipe["ingredients_detailed"][INDEX]
    norm = recipe["ingredients_normalized"][INDEX]

    # Strict pre-change checks
    assert detail.get("name") == "long green peppers"
    assert norm.get("original") == "long green peppers"
    assert norm.get("status") == "needs_review"
    assert norm.get("id") is None
    assert not norm.get("components")
    assert not norm.get("alternatives")
    assert detail.get("ingredient_id") is None
    assert detail.get("canonical_name") is None

    matching_ingredients = [
        item for item in ingredients_data["ingredients"]
        if item.get("id") == INGREDIENT_ID
    ]
    assert len(matching_ingredients) == 1

    # Confirm the canonical entry is the expected green bell pepper.
    names = matching_ingredients[0].get("names", {}).get("en", [])
    assert CANONICAL_NAME in names

    # Backups before modification
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    recipe_backup = RECIPE_FILE.with_name(
        f"{RECIPE_FILE.stem}.backup_batch7_greenpepper_{timestamp}.json"
    )
    ingredient_backup = INGREDIENT_FILE.with_name(
        f"{INGREDIENT_FILE.stem}.backup_batch7_greenpepper_{timestamp}.json"
    )

    shutil.copy2(RECIPE_FILE, recipe_backup)
    shutil.copy2(INGREDIENT_FILE, ingredient_backup)

    # Update only the LB041 target record.
    detail["ingredient_id"] = INGREDIENT_ID
    detail["canonical_name"] = CANONICAL_NAME

    norm["id"] = INGREDIENT_ID
    norm["canonical_name"] = CANONICAL_NAME
    norm["status"] = "matched"
    norm["mapping_note"] = NOTE

    validate(recipes_data, ingredients_data)
    print("In-memory validation passed.")

    temp_path = save_json_temp(recipes_data, RECIPE_FILE)

    try:
        temp_data = load_json(temp_path)
        validate(temp_data, ingredients_data)
        print("Temporary-file validation passed.")

        os.replace(temp_path, RECIPE_FILE)

        final_data = load_json(RECIPE_FILE)
        validate(final_data, ingredients_data)
        print("Final on-disk validation passed.")

    finally:
        if temp_path.exists():
            temp_path.unlink()

    print("\n" + "=" * 65)
    print("BATCH 7A COMPLETED SUCCESSFULLY")
    print("=" * 65)
    print("Recipe: LB041 - Kafta Meshwiyeh")
    print("Original: long green peppers")
    print("Mapped to: ING075 - green bell pepper")
    print("Status: matched (approximation)")
    print("Ingredient dictionary: unchanged")
    print("Other recipes: unchanged")
    print(f"\nRecipe backup: {recipe_backup}")
    print(f"Ingredient backup: {ingredient_backup}")

if __name__ == "__main__":
    main()
