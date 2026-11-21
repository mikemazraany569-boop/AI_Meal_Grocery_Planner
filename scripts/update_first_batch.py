
import json

path = "data/recipes/lebanese_recipes_enriched.json"

with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

target_ids = ["LB009", "LB010", "LB012", "LB013", "LB014"]

for recipe in data["recipes"]:
    if recipe["id"] in target_ids:
        print("\n" + "=" * 60)
        print(recipe["id"], "-", recipe["name_en"])

        print("Ingredients:")

        for item in recipe.get("ingredients_detailed", []):
            print(
                f"- {item['name']} "
                f"| Quantity: {item.get('quantity')} "
                f"| Unit: {item.get('unit')}"
            )
