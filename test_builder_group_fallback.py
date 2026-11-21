
import json
from pathlib import Path

from src.rag.recipe_document_builder import RecipeDocumentBuilder


RECIPE_FILE = Path("data/recipes/lebanese_recipes_enriched.json")

TARGET_IDS = ["LB042", "LB043", "LB044", "LB045"]

with RECIPE_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

recipes = (
    data
    if isinstance(data, list)
    else data.get("recipes", data.get("dishes", []))
)

builder = RecipeDocumentBuilder()
documents = builder.build_documents(recipes)

document_by_id = {
    doc["metadata"]["id"]: doc
    for doc in documents
}

print("=" * 65)
print("BUILDER GROUP FALLBACK TEST — READ ONLY")
print("=" * 65)

for recipe_id in TARGET_IDS:
    document = document_by_id.get(recipe_id)

    if document is None:
        print(f"\nERROR: {recipe_id} missing from documents")
        continue

    metadata = document["metadata"]

    print(f"\n{recipe_id} — {metadata['name_en']}")
    print("Ingredient IDs:", len(metadata["ingredient_ids"]))
    print("Total groups:", len(metadata["ingredient_groups"]))
    print("Required groups:", len(metadata["required_ingredient_groups"]))
    print("Optional groups:", len(metadata["optional_ingredient_groups"]))

    print("Groups:", metadata["ingredient_groups"])

    assert metadata["ingredient_groups"], (
        f"{recipe_id} still has no ingredient groups"
    )

    assert (
        len(metadata["required_ingredient_groups"])
        + len(metadata["optional_ingredient_groups"])
        == len(metadata["ingredient_groups"])
    ), f"{recipe_id}: group classification mismatch"

print("\n" + "=" * 65)
print("TEST COMPLETED")
print("No files modified.")
