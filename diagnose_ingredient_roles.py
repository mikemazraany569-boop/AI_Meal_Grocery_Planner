
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

RECIPES_PATH = (
    PROJECT_ROOT
    / "data"
    / "recipes"
    / "lebanese_recipes_enriched.json"
)

DOCUMENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "vector_store"
    / "recipes.json"
)

TARGET_IDS = ["LB003", "LB011", "LB020"]

with RECIPES_PATH.open("r", encoding="utf-8") as file:
    recipe_data = json.load(file)

recipes = (
    recipe_data.get("recipes", [])
    if isinstance(recipe_data, dict)
    else recipe_data
)

with DOCUMENTS_PATH.open("r", encoding="utf-8") as file:
    documents = json.load(file)

recipe_lookup = {
    recipe["id"]: recipe
    for recipe in recipes
}

document_lookup = {
    document["metadata"]["id"]: document
    for document in documents
}

print("=" * 70)
print("INGREDIENT ROLE DIAGNOSTIC — READ ONLY")
print("=" * 70)

for recipe_id in TARGET_IDS:

    recipe = recipe_lookup.get(recipe_id)
    document = document_lookup.get(recipe_id)

    if not recipe or not document:
        print(f"\n{recipe_id}: NOT FOUND")
        continue

    print(f"\n{recipe_id} — {recipe.get('name_en')}")
    print("-" * 70)

    print("\nOriginal ingredients:")
    for item in recipe.get("ingredients_original", []):
        print(" ", item)

    print("\nDetailed ingredient records:")

    for item in recipe.get("ingredients_detailed", []):

        if not isinstance(item, dict):
            continue

        print({
            "name": item.get("name"),
            "ingredient_id": item.get("ingredient_id"),
            "usage": item.get("usage"),
            "optional": item.get("optional"),
            "quantity": item.get("quantity"),
        })

    print("\nNormalized ingredient records:")

    for item in recipe.get("ingredients_normalized", []):

        if not isinstance(item, dict):
            continue

        print({
            "original": item.get("original"),
            "id": item.get("id"),
            "canonical_name": item.get("canonical_name"),
            "components": item.get("components"),
            "alternatives": item.get("alternatives"),
            "optional": item.get("optional"),
        })

    metadata = document["metadata"]

    print("\nSaved metadata keys:")
    print(list(metadata.keys()))

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETED — NO FILES MODIFIED")
print("=" * 70)
