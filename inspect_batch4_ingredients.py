import json
from pathlib import Path

path = Path("data/ingredients/ingredients_multilingual.json")

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

lookup_ids = ["ING006", "ING022", "ING032", "ING050", "ING081"]

print("=" * 65)
print("BATCH 4 EXISTING INGREDIENT INSPECTION")
print("=" * 65)

for ingredient in data["ingredients"]:
    if ingredient["id"] in lookup_ids:
        print(f"\n{ingredient['id']}")
        print(json.dumps(ingredient, ensure_ascii=False, indent=2))

print("\n" + "=" * 65)
print("NEW INGREDIENTS ING092–ING100")
print("=" * 65)

for ingredient in data["ingredients"]:
    number = int(ingredient["id"][3:])
    if 92 <= number <= 100:
        print(f"\n{ingredient['id']}")
        print(json.dumps(ingredient, ensure_ascii=False, indent=2))