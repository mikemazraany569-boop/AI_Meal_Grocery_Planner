
import json
from pathlib import Path
from collections import Counter

from src.rag.recipe_document_builder import RecipeDocumentBuilder

BASE = Path(__file__).resolve().parent

RECIPE_FILE = BASE / "data/recipes/lebanese_recipes_enriched.json"
INGREDIENT_FILE = BASE / "data/ingredients/ingredients_multilingual.json"

with RECIPE_FILE.open("r", encoding="utf-8") as f:
    recipes = json.load(f)["recipes"]

builder = RecipeDocumentBuilder(INGREDIENT_FILE)
documents = builder.build_documents(recipes)

print("=" * 65)
print("RAG DOCUMENT AUDIT — READ ONLY")
print("=" * 65)

print("Recipes loaded:", len(recipes))
print("Documents built:", len(documents))

document_ids = [
    doc["metadata"]["id"]
    for doc in documents
]

print("Unique document IDs:", len(set(document_ids)))
print("Duplicate IDs:", [
    recipe_id
    for recipe_id, count in Counter(document_ids).items()
    if count > 1
])

print("\n--- INGREDIENT MAPPING AUDIT ---")

top_level_mappings = []
missing_from_groups = []

for recipe in recipes:
    recipe_id = recipe.get("id")

    normalized = recipe.get("ingredients_normalized", [])
    detailed = recipe.get("ingredients_detailed", [])

    document = next(
        (d for d in documents if d["metadata"]["id"] == recipe_id),
        None
    )

    if document is None:
        continue

    indexed_ids = set(document["metadata"]["ingredient_ids"])

    for index, item in enumerate(normalized):
        if item.get("id"):
            top_level_mappings.append(
                (recipe_id, index, item["original"], item["id"])
            )

            if item["id"] not in indexed_ids:
                missing_from_groups.append(
                    (recipe_id, item["original"], item["id"])
                )

    for item in detailed:
        ingredient_id = item.get("ingredient_id")

        if ingredient_id and ingredient_id not in indexed_ids:
            print(
                "DETAILED ID NOT IN DOCUMENT:",
                recipe_id,
                item.get("name"),
                ingredient_id
            )

print("Top-level normalized mappings:", len(top_level_mappings))
print("Potentially omitted mappings:", len(missing_from_groups))

for record in missing_from_groups:
    print("OMITTED:", record)

print("\n--- DOCUMENT METADATA AUDIT ---")

missing_recipe_metadata = [
    doc["metadata"]["id"]
    for doc in documents
    if not isinstance(doc["metadata"].get("recipe"), dict)
]

missing_instructions = [
    doc["metadata"]["id"]
    for doc in documents
    if not doc["metadata"].get("has_instructions")
]

print("Missing original recipe metadata:", missing_recipe_metadata)
print("Recipes without instructions:", missing_instructions)

print("\n--- COMPLETED ---")
print("No files modified.")
