
import json
from pathlib import Path

path = Path("data/ingredients/ingredients_multilingual.json")

with path.open(encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]

terms = [
    "zucchini", "courgette", "grape leaves", "vine leaves",
    "white beans", "haricot", "coriander", "cilantro",
    "chicken stock", "vegetables", "mint", "seven spices",
    "meat", "pepper", "tomato juice", "dough",
    "lettuce", "cabbage", "sweet pepper"
]

for term in terms:
    print(f"\nSEARCH: {term}")
    found = False

    for ingredient in ingredients:
        names = ingredient.get("names", {})
        all_names = [
            name
            for language_names in names.values()
            for name in language_names
        ]

        if any(
            term.casefold() in name.casefold()
            or name.casefold() in term.casefold()
            for name in all_names
        ):
            print(
                ingredient["id"],
                names.get("en", []),
                names.get("ar", []),
                names.get("fr", [])
            )
            found = True

    if not found:
        print("No direct dictionary candidate found.")
