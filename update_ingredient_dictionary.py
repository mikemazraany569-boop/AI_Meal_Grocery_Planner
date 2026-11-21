
import json
from pathlib import Path

path = Path("data/ingredients/ingredients_multilingual.json")

with path.open(encoding="utf-8") as f:
    data = json.load(f)

ingredients = data["ingredients"]

new_ingredients = [
    {
        "id": "ING076",
        "names": {
            "en": ["zucchini", "courgette", "courgettes"],
            "ar": ["كوسا"],
            "fr": ["courgette", "courgettes"]
        }
    },
    {
        "id": "ING077",
        "names": {
            "en": ["grape leaves", "vine leaves"],
            "ar": ["ورق عنب", "ورق العنب"],
            "fr": ["feuilles de vigne"]
        }
    },
    {
        "id": "ING078",
        "names": {
            "en": ["tomato juice"],
            "ar": ["عصير الطماطم", "عصير البندورة"],
            "fr": ["jus de tomate"]
        }
    },
    {
        "id": "ING079",
        "names": {
            "en": ["chicken stock", "chicken broth"],
            "ar": ["مرق الدجاج"],
            "fr": ["bouillon de poulet"]
        }
    }
]

existing_ids = {item["id"] for item in ingredients}

for item in new_ingredients:
    if item["id"] not in existing_ids:
        ingredients.append(item)
        print("Added:", item["id"], item["names"]["en"][0])
    else:
        print("Already exists:", item["id"])

data["ingredients"] = ingredients

with path.open("w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\nIngredient dictionary updated.")
print("Total ingredients:", len(ingredients))
