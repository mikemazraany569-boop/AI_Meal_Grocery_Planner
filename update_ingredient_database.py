
import json
from pathlib import Path

project_root = Path(__file__).resolve().parent

database_path = (
    project_root
    / "data"
    / "ingredients"
    / "ingredients_multilingual.json"
)

with database_path.open("r", encoding="utf-8") as file:
    data = json.load(file)

ingredients = data["ingredients"]

by_id = {item["id"]: item for item in ingredients}

# Add aliases to existing canonical ingredients.
alias_updates = {
    "ING004": [
        "dried chickpeas (not canned)",
        "whole chickpeas",
    ],
    "ING011": [
        "large globe aubergines",
    ],
    "ING018": [
        "fine bulgur",
    ],
    "ING020": [
        "iced water",
    ],
    "ING025": [
        "strained yoghurt",
    ],
    "ING064": [
        "green pepper",
    ],
}

for ingredient_id, aliases in alias_updates.items():
    names = by_id[ingredient_id]["names"]["en"]

    for alias in aliases:
        if alias not in names:
            names.append(alias)

# Add genuinely distinct ingredients.
new_ingredients = [
    {
        "id": "ING067",
        "names": {
            "en": [
                "flatbread",
                "Lebanese flatbread",
                "lavash",
                "Lebanese flatbread or lavash",
            ],
            "ar": [],
            "fr": [],
        },
    },
    {
        "id": "ING068",
        "names": {
            "en": ["baking powder"],
            "ar": [],
            "fr": [],
        },
    },
    {
        "id": "ING069",
        "names": {
            "en": ["ground coriander", "coriander powder"],
            "ar": [],
            "fr": [],
        },
    },
    {
        "id": "ING070",
        "names": {
            "en": ["ground red pepper"],
            "ar": [],
            "fr": [],
        },
    },
    {
        "id": "ING071",
        "names": {
            "en": ["purslane"],
            "ar": [],
            "fr": [],
        },
    },
    {
        "id": "ING072",
        "names": {
            "en": ["sunflower oil"],
            "ar": [],
            "fr": [],
        },
    },
    {
        "id": "ING073",
        "names": {
            "en": ["sesame seeds", "white sesame seeds"],
            "ar": [],
            "fr": [],
        },
    },
    {
        "id": "ING074",
        "names": {
            "en": ["seven spices", "Lebanese seven spices"],
            "ar": [],
            "fr": [],
        },
    },
]

existing_ids = set(by_id)

for ingredient in new_ingredients:
    if ingredient["id"] not in existing_ids:
        ingredients.append(ingredient)

# Save the updated database.
with database_path.open("w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

print("INGREDIENT DATABASE UPDATED")
print("Total canonical ingredients:", len(ingredients))
print("New IDs: ING067 to ING074")
print("Existing IDs preserved.")
