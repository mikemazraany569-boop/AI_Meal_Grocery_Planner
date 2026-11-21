
import json
from pathlib import Path

path = Path("data/ingredients/ingredients_multilingual.json")
backup = Path("data/ingredients/ingredients_multilingual_before_batch4_existing_aliases.json")

if backup.exists():
    raise FileExistsError(f"Backup already exists: {backup}")

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

aliases_to_add = {
    "ING032": ["frozen spinach", "frozen leaf spinach"],
    "ING050": ["cumin powder"],
    "ING006": ["medium-grain rice"],
    "ING022": ["white granulated sugar"],
    "ING081": ["corn flour"],
}

ingredients_by_id = {
    item["id"]: item for item in data["ingredients"]
}

# Create a backup before modifying anything.
backup.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

added = 0

for ingredient_id, aliases in aliases_to_add.items():
    ingredient = ingredients_by_id.get(ingredient_id)

    if ingredient is None:
        raise ValueError(f"Ingredient ID not found: {ingredient_id}")

    english_names = ingredient["names"].setdefault("en", [])

    for alias in aliases:
        if alias.lower() not in {name.lower() for name in english_names}:
            english_names.append(alias)
            added += 1
            print(f"Added: {alias} -> {ingredient_id}")
        else:
            print(f"Already exists: {alias} -> {ingredient_id}")

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print("BATCH 4 EXISTING ALIASES COMPLETED")
print("=" * 60)
print(f"Aliases added: {added}")
print(f"Total canonical ingredients: {len(data['ingredients'])}")
print(f"Backup: {backup.name}")
