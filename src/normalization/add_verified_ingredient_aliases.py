
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATABASE_PATH = (
    PROJECT_ROOT
    / "data"
    / "ingredients"
    / "ingredients_multilingual.json"
)

# Only aliases that clearly refer to the same ingredient.
ALIASES_TO_ADD = {
    "ING003": [
        "Italian parsley",
    ],
    "ING004": [
        "dried chickpeas",
    ],
    "ING008": [
        "garlic cloves minced",
        "garlic cloves crushed",
        "garlic cloves peeled",
        "freshly peeled crushed garlic cloves",
    ],
    "ING009": [
        "lemon juice",
        "juice of lemon",
        "juice of lemons",
        "freshly squeezed lemon juice",
    ],
    "ING015": [
        "whole black peppercorns",
    ],
    "ING018": [
        "bulgur cracked wheat",
    ],
    "ING019": [
        "multi-purpose flour",
    ],
    "ING021": [
        "baker's yeast",
        "baker’s yeast",
    ],
    "ING029": [
        "dry peeled fava beans",
    ],
    "ING047": [
        "green cardamom",
        "whole green cardamoms",
    ],
    "ING048": [
        "cinnamon powder",
        "ground cinnamon",
    ],
    "ING054": [
        "frozen green beans",
    ],
    "ING063": [
        "small pearl onions",
    ],
}


with DATABASE_PATH.open("r", encoding="utf-8") as file:
    data = json.load(file)

ingredients = data["ingredients"]

ingredients_by_id = {
    ingredient["id"]: ingredient
    for ingredient in ingredients
}

# Build a lookup to prevent aliases from belonging to two ingredients.
alias_owner = {}

for ingredient in ingredients:
    for language, aliases in ingredient.get("names", {}).items():
        for alias in aliases:
            alias_owner[alias.strip().casefold()] = ingredient["id"]

added_count = 0

for ingredient_id, new_aliases in ALIASES_TO_ADD.items():

    if ingredient_id not in ingredients_by_id:
        raise ValueError(f"Unknown ingredient ID: {ingredient_id}")

    ingredient = ingredients_by_id[ingredient_id]
    english_names = ingredient.setdefault("names", {}).setdefault("en", [])

    for alias in new_aliases:
        key = alias.strip().casefold()

        if key in alias_owner:
            if alias_owner[key] != ingredient_id:
                raise ValueError(
                    f"Alias conflict: {alias} belongs to "
                    f"{alias_owner[key]}, not {ingredient_id}"
                )
            continue

        english_names.append(alias)
        alias_owner[key] = ingredient_id
        added_count += 1

with DATABASE_PATH.open("w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.write("\n")

print("VERIFIED ALIASES ADDED")
print("New aliases:", added_count)
print("Total ingredients:", len(ingredients))
