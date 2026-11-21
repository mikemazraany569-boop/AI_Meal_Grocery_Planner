
import json
from pathlib import Path
from collections import Counter, defaultdict

RECIPE_FILE = Path("data/recipes/lebanese_recipes_enriched.json")
DOCUMENT_FILE = Path("data/vector_store/recipes.json")

with RECIPE_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

recipes = (
    data
    if isinstance(data, list)
    else data.get("recipes", data.get("dishes", []))
)

with DOCUMENT_FILE.open("r", encoding="utf-8") as file:
    documents = json.load(file)

recipe_by_id = {
    recipe["id"]: recipe
    for recipe in recipes
}

TARGET_IDS = [
    "LB004", "LB006", "LB009", "LB011", "LB012",
    "LB015", "LB037", "LB038", "LB049"
]

print("=" * 70)
print("DUPLICATE INGREDIENT GROUP INSPECTION — READ ONLY")
print("=" * 70)

for document in documents:
    metadata = document["metadata"]
    recipe_id = metadata["id"]

    if recipe_id not in TARGET_IDS:
        continue

    recipe = recipe_by_id.get(recipe_id, {})
    groups = metadata.get("ingredient_groups", [])

    occurrences = defaultdict(list)

    for index, group in enumerate(groups):
        for ingredient_id in group:
            occurrences[ingredient_id].append(index)

    duplicates = {
        ingredient_id: indexes
        for ingredient_id, indexes in occurrences.items()
        if len(indexes) > 1
    }

    if not duplicates:
        continue

    print(f"\n{recipe_id} — {metadata.get('name_en')}")

    for ingredient_id, indexes in duplicates.items():
        print(f"\n  Ingredient ID: {ingredient_id}")
        print("  Group positions:", indexes)

        matching_records = [
            item
            for item in recipe.get("ingredients_detailed", [])
            if isinstance(item, dict)
            and item.get("ingredient_id") == ingredient_id
        ]

        print("  Detailed records:")

        for item in matching_records:
            print(
                "   ",
                {
                    "name": item.get("name"),
                    "quantity": item.get("quantity"),
                    "unit": item.get("unit"),
                    "usage": item.get("usage"),
                    "optional": item.get("optional", False),
                }
            )

        normalized = recipe.get("ingredients_normalized", [])

        print("  Normalized records containing this ID:")

        for index, item in enumerate(normalized):
            if not isinstance(item, dict):
                continue

            ids = []

            if item.get("id"):
                ids.append(item["id"])

            for component in item.get("components", []):
                if isinstance(component, dict) and component.get("id"):
                    ids.append(component["id"])

            for alternative in item.get("alternatives", []):
                if isinstance(alternative, dict) and alternative.get("id"):
                    ids.append(alternative["id"])

            if ingredient_id in ids:
                print(
                    f"    Normalized record {index}: "
                    f"{item.get('original', item)}"
                )

print("\n" + "=" * 70)
print("Inspection completed. No files modified.")
