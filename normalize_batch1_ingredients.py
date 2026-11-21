
import json
import shutil
import re
from pathlib import Path
from datetime import date


ROOT = Path(__file__).resolve().parent

RECIPE_FILE = (
    ROOT / "data" / "recipes" / "lebanese_recipes_enriched.json"
)

INGREDIENT_FILE = (
    ROOT / "data" / "ingredients" / "ingredients_multilingual.json"
)

recipe_backup = RECIPE_FILE.with_name(
    "lebanese_recipes_enriched_before_batch1_normalization.json"
)

ingredient_backup = INGREDIENT_FILE.with_name(
    "ingredients_multilingual_before_batch1_normalization.json"
)


# ------------------------------------------------------------
# LOAD FILES
# ------------------------------------------------------------

with open(RECIPE_FILE, "r", encoding="utf-8") as f:
    recipe_data = json.load(f)

with open(INGREDIENT_FILE, "r", encoding="utf-8") as f:
    ingredient_data = json.load(f)

ingredients = ingredient_data["ingredients"]
recipes = recipe_data["recipes"]


# ------------------------------------------------------------
# BUILD LOOKUP
# ------------------------------------------------------------

def build_lookup():
    lookup = {}

    for item in ingredients:
        for language, aliases in item.get("names", {}).items():
            for alias in aliases:
                lookup[alias.strip().lower()] = item

    return lookup


lookup = build_lookup()


# ------------------------------------------------------------
# ADD ALIASES TO EXISTING INGREDIENTS
# ------------------------------------------------------------

alias_updates = {
    "ING023": ["lean raw lamb"],
    "ING024": ["lean minced beef"],
    "ING025": ["plain yogurt"]
}

for ingredient_id, aliases in alias_updates.items():

    ingredient = next(
        (
            item for item in ingredients
            if item["id"] == ingredient_id
        ),
        None
    )

    if ingredient is None:
        raise ValueError(
            f"Ingredient ID not found: {ingredient_id}"
        )

    english_names = ingredient["names"].setdefault("en", [])

    for alias in aliases:
        if alias.lower() not in [
            name.lower() for name in english_names
        ]:
            english_names.append(alias)
            
# REBUILD LOOKUP AFTER ADDING ALIASES
lookup = build_lookup()

# ------------------------------------------------------------
# GENERATE NEW UNIQUE INGREDIENT IDS
# ------------------------------------------------------------

existing_numbers = [
    int(match.group(1))
    for item in ingredients
    if (match := re.fullmatch(r"ING(\d+)", item["id"]))
]

next_number = max(existing_numbers, default=0) + 1


def add_ingredient(name):
    global next_number

    existing = lookup.get(name.lower())

    if existing:
        return existing

    ingredient_id = f"ING{next_number:03d}"
    next_number += 1

    new_ingredient = {
        "id": ingredient_id,
        "names": {
            "en": [name],
            "ar": [],
            "fr": []
        }
    }

    ingredients.append(new_ingredient)
    lookup[name.lower()] = new_ingredient

    print(f"Added {ingredient_id}: {name}")

    return new_ingredient


new_ingredients = [
    "cornstarch",
    "bitter orange juice",
    "mandarin juice",
    "orange juice"
]

for name in new_ingredients:
    add_ingredient(name)


# ------------------------------------------------------------
# NORMALIZE THE FIVE NEW RECIPES
# ------------------------------------------------------------

target_ids = {
    "LB031", "LB032", "LB033", "LB034", "LB035"
}

matched_count = 0
review_count = 0


for recipe in recipes:

    if recipe["id"] not in target_ids:
        continue

    normalized_records = []

    for detailed in recipe["ingredients_detailed"]:

        original = detailed["name"]
        match = lookup.get(original.strip().lower())

        # Composite preparation: do not falsely map it
        if original.strip().lower() == "kibbeh shells":
            detailed["ingredient_id"] = None
            detailed["canonical_name"] = None

            normalized_records.append({
                "original": original,
                "components": [],
                "alternatives": [],
                "status": "needs_review"
            })

            review_count += 1
            continue

        if match:

            detailed["ingredient_id"] = match["id"]
            detailed["canonical_name"] = (
                match["names"]["en"][0]
            )

            normalized_records.append({
                "original": original,
                "components": [{
                    "original": original,
                    "id": match["id"],
                    "canonical_name": match["names"]["en"][0],
                    "status": "matched"
                }],
                "alternatives": [],
                "status": "matched"
            })

            matched_count += 1

        else:

            detailed["ingredient_id"] = None
            detailed["canonical_name"] = None

            normalized_records.append({
                "original": original,
                "components": [],
                "alternatives": [],
                "status": "needs_review"
            })

            review_count += 1

    recipe["ingredients_normalized"] = normalized_records

    # Document the composite preparation
    if recipe["id"] in {"LB033", "LB034"}:
        note = (
            "Kibbeh shells are a composite preparation. "
            "They remain needs_review until their component "
            "ingredients and quantities are explicitly modeled."
        )

        if note not in recipe["notes"]:
            recipe["notes"].append(note)


# ------------------------------------------------------------
# BACKUP AND SAVE
# ------------------------------------------------------------

shutil.copy2(RECIPE_FILE, recipe_backup)
shutil.copy2(INGREDIENT_FILE, ingredient_backup)

with open(INGREDIENT_FILE, "w", encoding="utf-8") as f:
    json.dump(ingredient_data, f, ensure_ascii=False, indent=4)

with open(RECIPE_FILE, "w", encoding="utf-8") as f:
    json.dump(recipe_data, f, ensure_ascii=False, indent=4)


# ------------------------------------------------------------
# REPORT
# ------------------------------------------------------------

print("\n" + "=" * 60)
print("BATCH 1 INGREDIENT NORMALIZATION")
print("=" * 60)

print("New canonical ingredients:", len(new_ingredients))
print("Matched ingredient records:", matched_count)
print("Records requiring review:", review_count)

print("\nNew ingredient IDs:")

for name in new_ingredients:
    item = lookup[name]
    print(item["id"], "-", name)

print("\nRecipe summary:")

for recipe in recipes:
    if recipe["id"] in target_ids:
        matched = sum(
            item["status"] == "matched"
            for item in recipe["ingredients_normalized"]
        )

        total = len(recipe["ingredients_normalized"])

        print(
            f"{recipe['id']} - {recipe['name_en']}: "
            f"{matched}/{total} matched"
        )

print("\nRecipe backup:", recipe_backup)
print("Ingredient backup:", ingredient_backup)

print("\nNormalization completed successfully.")
