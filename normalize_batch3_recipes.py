
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RECIPE_FILE = (
    ROOT / "data" / "recipes"
    / "lebanese_recipes_enriched.json"
)

BACKUP_FILE = RECIPE_FILE.with_name(
    "lebanese_recipes_enriched_before_batch3_normalization.json"
)

INGREDIENT_FILE = (
    ROOT / "data" / "ingredients"
    / "ingredients_multilingual.json"
)

BATCH_IDS = {"LB041", "LB042", "LB043", "LB044", "LB045"}

# These records are intentionally not mapped automatically.
UNRESOLVED = {
    "LB041": {
        "minced lamb or beef",
        "long green peppers",
    }
}


def build_lookup(ingredient_data):
    lookup = {}

    for ingredient in ingredient_data:
        names = ingredient.get("names", {})
        english_names = names.get("en", [])

        canonical_name = (
            english_names[0]
            if english_names
            else ingredient["id"]
        )

        for language in ("en", "ar", "fr"):
            for name in names.get(language, []):
                lookup[name.strip().lower()] = {
                    "id": ingredient["id"],
                    "canonical_name": canonical_name,
                }

    return lookup


# Load data
with open(RECIPE_FILE, "r", encoding="utf-8") as f:
    recipe_data = json.load(f)

with open(INGREDIENT_FILE, "r", encoding="utf-8") as f:
    ingredient_data = json.load(f)

recipes = recipe_data["recipes"]
lookup = build_lookup(ingredient_data["ingredients"])

recipes_by_id = {
    recipe["id"]: recipe
    for recipe in recipes
}

missing_ids = BATCH_IDS - set(recipes_by_id)

if missing_ids:
    raise ValueError(
        f"Missing recipes: {sorted(missing_ids)}"
    )

# Validate every ingredient before making changes
for recipe_id in sorted(BATCH_IDS):
    recipe = recipes_by_id[recipe_id]

    for item in recipe["ingredients_detailed"]:
        name = item["name"].strip().lower()

        if name in UNRESOLVED.get(recipe_id, set()):
            continue

        if name not in lookup:
            raise ValueError(
                f"Unrecognized ingredient: {recipe_id} - {item['name']}"
            )

# Refuse to overwrite an existing backup
if BACKUP_FILE.exists():
    raise FileExistsError(
        f"Backup already exists: {BACKUP_FILE}"
    )

shutil.copy2(RECIPE_FILE, BACKUP_FILE)

# Normalize recipes
for recipe_id in sorted(BATCH_IDS):
    recipe = recipes_by_id[recipe_id]

    normalized = []

    for item in recipe["ingredients_detailed"]:
        original_name = item["name"]
        key = original_name.strip().lower()

        # Special handling for minced lamb OR beef
        if recipe_id == "LB041" and key == "minced lamb or beef":
            alternatives = [
                {
                    "ingredient_id": "ING023",
                    "canonical_name": "lamb",
                },
                {
                    "ingredient_id": "ING024",
                    "canonical_name": "beef",
                },
            ]

            item["ingredient_id"] = None
            item["canonical_name"] = None

            normalized.append({
                "original": original_name,
                "status": "alternatives",
                "components": [],
                "alternatives": alternatives,
            })
            continue

        # Keep long green peppers unresolved
        if recipe_id == "LB041" and key == "long green peppers":
            item["ingredient_id"] = None
            item["canonical_name"] = None

            normalized.append({
                "original": original_name,
                "status": "needs_review",
                "components": [],
                "alternatives": [],
            })
            continue

        match = lookup[key]

        item["ingredient_id"] = match["id"]
        item["canonical_name"] = match["canonical_name"]

        normalized.append({
            "original": original_name,
            "status": "matched",
            "components": [
                {
                    "ingredient_id": match["id"],
                    "canonical_name": match["canonical_name"],
                }
            ],
            "alternatives": [],
        })

    recipe["ingredients_normalized"] = normalized

# Save updated recipes
with open(RECIPE_FILE, "w", encoding="utf-8") as f:
    json.dump(
        recipe_data,
        f,
        ensure_ascii=False,
        indent=2
    )

print("\n" + "=" * 65)
print("BATCH 3 NORMALIZATION COMPLETED")
print("=" * 65)

for recipe_id in sorted(BATCH_IDS):
    recipe = recipes_by_id[recipe_id]

    statuses = {}

    for item in recipe["ingredients_normalized"]:
        status = item["status"]
        statuses[status] = statuses.get(status, 0) + 1

    print(
        f"{recipe_id} - {recipe['name_en']} | "
        f"Ingredients: {len(recipe['ingredients_detailed'])} | "
        f"Statuses: {statuses}"
    )

print(f"\nBackup: {BACKUP_FILE.name}")
