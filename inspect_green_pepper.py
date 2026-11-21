
import json
from pathlib import Path

path = (
    Path(__file__).resolve().parent
    / "data"
    / "ingredients"
    / "ingredients_multilingual.json"
)

with path.open("r", encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]

print("=" * 70)
print("GREEN PEPPER DICTIONARY INSPECTION")
print("=" * 70)

terms = [
    "green pepper",
    "green peppers",
    "long green pepper",
    "long green peppers",
    "bell pepper",
    "capsicum",
    "sweet pepper",
    "pepper",
]

matches = []

for ingredient in ingredients:
    names = ingredient.get("names", {})
    all_names = []

    for language, aliases in names.items():
        if isinstance(aliases, list):
            all_names.extend(aliases)
        elif isinstance(aliases, str):
            all_names.append(aliases)

    matching = [
        name for name in all_names
        if any(term in name.lower() for term in terms)
    ]

    if matching:
        matches.append(ingredient)

for ingredient in matches:
    print(f"\nID: {ingredient.get('id')}")
    print(f"Names: {ingredient.get('names')}")

print("\n" + "=" * 70)
print(f"Matching canonical ingredients: {len(matches)}")
print("No files were modified.")
print("=" * 70)
