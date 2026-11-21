
import json
from pathlib import Path

RECIPE_FILE = Path("data/recipes/lebanese_recipes_enriched.json")
DOCUMENT_FILE = Path("data/vector_store/recipes.json")

with RECIPE_FILE.open("r", encoding="utf-8") as f:
    recipe_data = json.load(f)

recipes = (
    recipe_data
    if isinstance(recipe_data, list)
    else recipe_data.get("recipes", recipe_data.get("dishes", []))
)

with DOCUMENT_FILE.open("r", encoding="utf-8") as f:
    documents = json.load(f)

document_by_id = {
    doc["metadata"]["id"]: doc
    for doc in documents
}

print("=" * 65)
print("EMPTY INGREDIENT GROUP AUDIT — READ ONLY")
print("=" * 65)

empty_count = 0

for recipe in recipes:
    recipe_id = recipe.get("id")
    document = document_by_id.get(recipe_id)

    if not document:
        print("MISSING DOCUMENT:", recipe_id)
        continue

    metadata = document["metadata"]
    groups = metadata.get("required_ingredient_groups", [])
    optional_groups = metadata.get("optional_ingredient_groups", [])

    if groups or optional_groups:
        continue

    detailed = recipe.get("ingredients_detailed", [])

    detailed_ids = list(dict.fromkeys(
        item.get("ingredient_id")
        for item in detailed
        if isinstance(item, dict) and item.get("ingredient_id")
    ))

    if not detailed_ids:
        continue

    empty_count += 1

    print(f"\n{recipe_id} — {recipe.get('name_en')}")
    print("Normalized records:", len(recipe.get("ingredients_normalized", [])))
    print("Detailed records:", len(detailed))
    print("Detailed ingredient IDs:", detailed_ids)
    print("Detailed names:", [
        item.get("name")
        for item in detailed
        if isinstance(item, dict)
    ])

print("\nRecipes with detailed IDs but no groups:", empty_count)
print("\nAudit completed. No files modified.")
