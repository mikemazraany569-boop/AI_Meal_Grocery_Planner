
import json
from pathlib import Path
from collections import Counter

from src.rag.recipe_document_builder import RecipeDocumentBuilder


RECIPE_FILE = Path("data/recipes/lebanese_recipes_enriched.json")

with RECIPE_FILE.open("r", encoding="utf-8") as file:
    data = json.load(file)

recipes = (
    data
    if isinstance(data, list)
    else data.get("recipes", data.get("dishes", []))
)

builder = RecipeDocumentBuilder()
documents = builder.build_documents(recipes)

print("=" * 70)
print("INGREDIENT GROUP DEDUPLICATION TEST — READ ONLY")
print("=" * 70)

errors = []

for document in documents:
    metadata = document["metadata"]
    recipe_id = metadata["id"]

    groups = metadata["ingredient_groups"]
    required = metadata["required_ingredient_groups"]
    optional = metadata["optional_ingredient_groups"]

    flattened = [
        ingredient_id
        for group in groups
        for ingredient_id in group
    ]

    duplicates = [
        ingredient_id
        for ingredient_id, count in Counter(flattened).items()
        if count > 1
    ]

    if duplicates:
        errors.append(
            f"{recipe_id}: duplicate IDs {duplicates}"
        )

    if len(required) + len(optional) != len(groups):
        errors.append(
            f"{recipe_id}: classification count mismatch"
        )

    if set(flattened) != set(metadata["ingredient_ids"]):
        errors.append(
            f"{recipe_id}: group IDs and ingredient IDs differ"
        )

    if any(not group for group in groups):
        errors.append(
            f"{recipe_id}: empty ingredient group"
        )

print("\nTarget recipe results:")

for recipe_id in [
    "LB004", "LB006", "LB009", "LB011", "LB012",
    "LB015", "LB037", "LB038", "LB049"
]:
    document = next(
        (
            doc for doc in documents
            if doc["metadata"]["id"] == recipe_id
        ),
        None
    )

    if document is None:
        errors.append(f"{recipe_id}: missing document")
        continue

    metadata = document["metadata"]

    print(f"\n{recipe_id} — {metadata['name_en']}")
    print("Total groups:", len(metadata["ingredient_groups"]))
    print("Required groups:", len(metadata["required_ingredient_groups"]))
    print("Optional groups:", len(metadata["optional_ingredient_groups"]))

    print("Groups:", metadata["ingredient_groups"])

# Verify LB049 onion is required, not optional.
lb049 = next(
    doc for doc in documents
    if doc["metadata"]["id"] == "LB049"
)

lb049_metadata = lb049["metadata"]

if ["ING002"] not in lb049_metadata["required_ingredient_groups"]:
    errors.append("LB049: onion ING002 should be required")

if ["ING002"] in lb049_metadata["optional_ingredient_groups"]:
    errors.append("LB049: onion ING002 incorrectly classified as optional")

# Verify LB011 chickpeas appear only once in groups.
lb011 = next(
    doc for doc in documents
    if doc["metadata"]["id"] == "LB011"
)

chickpea_count = sum(
    group.count("ING004")
    for group in lb011["metadata"]["ingredient_groups"]
)

if chickpea_count != 1:
    errors.append(
        f"LB011: expected one chickpea group, got {chickpea_count}"
    )

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)
print("Recipes tested:", len(documents))
print("Validation errors:", len(errors))

if errors:
    print("\nERRORS:")
    for error in errors:
        print("-", error)
else:
    print("\nALL VALIDATIONS PASSED")

print("\nNo files modified.")
