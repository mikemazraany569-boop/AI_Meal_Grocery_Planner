
import json
from pathlib import Path
from collections import Counter

DOCUMENT_FILE = Path("data/vector_store/recipes.json")

with DOCUMENT_FILE.open("r", encoding="utf-8") as file:
    documents = json.load(file)

print("=" * 70)
print("RAG INGREDIENT GROUP CONSISTENCY AUDIT — READ ONLY")
print("=" * 70)

duplicate_group_count = 0
empty_group_count = 0
classification_errors = 0
id_mismatch_count = 0

for document in documents:
    metadata = document["metadata"]
    recipe_id = metadata["id"]
    name = metadata.get("name_en", "Unknown")

    groups = metadata.get("ingredient_groups", [])
    required = metadata.get("required_ingredient_groups", [])
    optional = metadata.get("optional_ingredient_groups", [])
    ingredient_ids = metadata.get("ingredient_ids", [])

    if not groups:
        empty_group_count += 1
        print(f"\nEMPTY GROUPS: {recipe_id} — {name}")

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
        duplicate_group_count += 1
        print(
            f"\nDUPLICATE GROUP IDS: {recipe_id} — {name}"
        )
        print("Duplicates:", duplicates)

    classified = required + optional

    if len(classified) != len(groups):
        classification_errors += 1
        print(
            f"\nCLASSIFICATION COUNT ERROR: {recipe_id} — {name}"
        )

    group_ids = set(flattened)
    metadata_ids = set(ingredient_ids)

    if not group_ids.issubset(metadata_ids):
        id_mismatch_count += 1
        print(
            f"\nGROUP/METADATA ID MISMATCH: {recipe_id} — {name}"
        )
        print("Missing from metadata:", sorted(group_ids - metadata_ids))

print("\n" + "=" * 70)
print("AUDIT SUMMARY")
print("=" * 70)
print("Documents:", len(documents))
print("Recipes with empty groups:", empty_group_count)
print("Recipes with duplicate ingredient IDs in groups:", duplicate_group_count)
print("Classification errors:", classification_errors)
print("Group/metadata ID mismatches:", id_mismatch_count)
print("\nAudit completed. No files modified.")
