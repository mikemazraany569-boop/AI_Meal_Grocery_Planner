
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILE = (
    ROOT / "data" / "ingredients"
    / "ingredients_multilingual.json"
)

BACKUP = FILE.with_name(
    "ingredients_multilingual_before_batch4.json"
)

# Confirmed aliases for existing canonical ingredients
ALIASES = {
    "ING002": [
        "medium onion",
        "medium onions",
        "caramelized onions",
    ],
    "ING008": [
        "small garlic cloves",
    ],
    "ING023": [
        "lamb leg",
        "lamb shoulder meat",
    ],
    "ING020": [
        "hot water",
    ],
    "ING046": [
        "large carrot",
    ],
    "ING040": [
        "small potato",
    ],
    "ING034": [
        "fried pita bread",
        "toasted pita bread",
    ],
}

# New canonical ingredients and their known English names.
# The script checks for possible existing equivalents first.
NEW_INGREDIENTS = {
    "freekeh": ["freekeh"],
    "peas": ["peas", "green peas", "frozen peas"],
    "tomato sauce": ["tomato sauce"],
    "curry powder": ["curry powder"],
    "spinach": [
        "spinach",
        "fresh spinach",
        "frozen spinach",
        "frozen leaf spinach",
    ],
    "chili flakes": ["chili flakes", "chilli flakes"],
    "cumin": ["cumin", "cumin powder", "ground cumin"],
    "rice": ["rice", "medium-grain rice", "jasmine rice"],
    "milk": ["milk", "full-cream milk", "full cream milk"],
    "sugar": ["sugar", "white granulated sugar"],
    "rose water": ["rose water"],
    "orange blossom water": ["orange blossom water"],
    "pistachios": ["pistachios", "pistachio"],
}


def normalize_name(value):
    return value.strip().lower()


# Load dictionary
with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]

by_id = {
    item["id"]: item
    for item in ingredients
}

if len(by_id) != len(ingredients):
    raise ValueError("Duplicate ingredient IDs already exist.")

# Validate alias targets
for ingredient_id in ALIASES:
    if ingredient_id not in by_id:
        raise ValueError(
            f"Ingredient ID not found: {ingredient_id}"
        )

# Build lookup of existing names
existing_names = {}

for ingredient in ingredients:
    for language in ("en", "ar", "fr"):
        for name in ingredient.get("names", {}).get(language, []):
            existing_names[normalize_name(name)] = ingredient["id"]

# Prepare additions before modifying the dictionary
aliases_to_add = []

for ingredient_id, aliases in ALIASES.items():
    names_en = by_id[ingredient_id].get("names", {}).get("en", [])

    for alias in aliases:
        key = normalize_name(alias)

        if key in existing_names:
            if existing_names[key] != ingredient_id:
                raise ValueError(
                    f"Alias conflict: {alias} already belongs to "
                    f"{existing_names[key]}, not {ingredient_id}"
                )
        elif key not in {
            normalize_name(name) for name in names_en
        }:
            aliases_to_add.append((ingredient_id, alias))

# Identify genuinely new ingredients and possible duplicates
new_records = []
possible_duplicates = []

next_number = max(
    int(match.group(1))
    for ingredient in ingredients
    if (match := re.fullmatch(r"ING(\d+)", ingredient["id"]))
) + 1

for canonical_name, aliases in NEW_INGREDIENTS.items():
    matches = {
        existing_names[normalize_name(alias)]
        for alias in aliases
        if normalize_name(alias) in existing_names
    }

    if matches:
        possible_duplicates.append(
            (canonical_name, sorted(matches))
        )
        continue

    ingredient_id = f"ING{next_number:03d}"
    next_number += 1

    new_records.append({
        "id": ingredient_id,
        "names": {
            "en": aliases,
            "ar": [],
            "fr": [],
        }
    })

# Stop if backup already exists
if BACKUP.exists():
    raise FileExistsError(
        f"Backup already exists: {BACKUP}"
    )

# Create backup
shutil.copy2(FILE, BACKUP)

# Add aliases
for ingredient_id, alias in aliases_to_add:
    by_id[ingredient_id].setdefault(
        "names", {}
    ).setdefault("en", []).append(alias)

# Add new canonical ingredients
ingredients.extend(new_records)

# Save dictionary
with open(FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Report
print("\n" + "=" * 65)
print("BATCH 4 INGREDIENT DICTIONARY UPDATE")
print("=" * 65)

print("\nALIASES ADDED:")
for ingredient_id, alias in aliases_to_add:
    print(f"  {alias} -> {ingredient_id}")

print("\nNEW CANONICAL INGREDIENTS:")
for item in new_records:
    print(
        f"  {item['id']} - {item['names']['en'][0]}"
    )

print("\nPOSSIBLE EXISTING INGREDIENTS - REVIEW:")
for name, matches in possible_duplicates:
    print(f"  {name} may already exist under {matches}")

print("\nSUMMARY")
print("Aliases added:", len(aliases_to_add))
print("New canonical ingredients:", len(new_records))
print("Possible duplicates skipped:", len(possible_duplicates))
print("Total dictionary ingredients:", len(ingredients))
print("Backup:", BACKUP.name)
