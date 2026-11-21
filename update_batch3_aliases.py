
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

FILE = (
    ROOT / "data" / "ingredients"
    / "ingredients_multilingual.json"
)

BACKUP = FILE.with_name(
    "ingredients_multilingual_before_batch3_final_aliases.json"
)

NEW_ALIASES = {
    "ING008": ["garlic clove"],
    "ING007": ["regular olive oil"],
    "ING020": ["boiled water", "cold water"],
}

# Load dictionary
with open(FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]

by_id = {
    ingredient["id"]: ingredient
    for ingredient in ingredients
}

# Validate all target IDs before changing anything
for ingredient_id in NEW_ALIASES:
    if ingredient_id not in by_id:
        raise ValueError(
            f"Ingredient ID not found: {ingredient_id}"
        )

# Create backup without overwriting an existing backup
if BACKUP.exists():
    raise FileExistsError(
        f"Backup already exists: {BACKUP}"
    )

with open(BACKUP, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Add aliases without creating duplicates
added = 0

for ingredient_id, aliases in NEW_ALIASES.items():
    names_en = by_id[ingredient_id].setdefault(
        "names", {}
    ).setdefault("en", [])

    for alias in aliases:
        if alias.lower() not in {
            name.lower() for name in names_en
        }:
            names_en.append(alias)
            added += 1
            print(f"Added: {alias} -> {ingredient_id}")
        else:
            print(f"Already exists: {alias} -> {ingredient_id}")

# Save updated dictionary
with open(FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 55)
print("BATCH 3 ALIAS UPDATE COMPLETED")
print("=" * 55)
print(f"New aliases added: {added}")
print(f"Backup created: {BACKUP.name}")
