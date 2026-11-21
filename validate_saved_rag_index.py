
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent

DOCUMENTS_PATH = (
    PROJECT_ROOT / "data" / "vector_store" / "recipes.json"
)

INDEX_PATH = (
    PROJECT_ROOT / "data" / "vector_store" / "recipes.index"
)

print("=" * 70)
print("SAVED RAG INDEX VALIDATION — READ ONLY")
print("=" * 70)

if not DOCUMENTS_PATH.exists():
    raise FileNotFoundError(DOCUMENTS_PATH)

if not INDEX_PATH.exists():
    raise FileNotFoundError(INDEX_PATH)

with DOCUMENTS_PATH.open("r", encoding="utf-8") as file:
    documents = json.load(file)

import faiss

index = faiss.read_index(str(INDEX_PATH))

errors = []

print(f"\nSaved documents: {len(documents)}")
print(f"FAISS vectors: {index.ntotal}")
print(f"Vector dimensions: {index.d}")
print(f"Index type: {type(index).__name__}")

if len(documents) != 50:
    errors.append(f"Expected 50 documents, found {len(documents)}")

if index.ntotal != len(documents):
    errors.append(
        f"FAISS/document count mismatch: {index.ntotal} vs {len(documents)}"
    )

ids = []
total_groups = 0

for document in documents:

    metadata = document.get("metadata", {})
    recipe_id = metadata.get("id", "UNKNOWN")

    ids.append(recipe_id)

    ingredient_ids = metadata.get("ingredient_ids", [])
    groups = metadata.get("ingredient_groups", [])
    required = metadata.get("required_ingredient_groups", [])
    optional = metadata.get("optional_ingredient_groups", [])

    flattened = [
        ingredient_id
        for group in groups
        for ingredient_id in group
    ]

    total_groups += len(groups)

    if len(flattened) != len(set(flattened)):
        errors.append(f"{recipe_id}: repeated IDs across groups")

    if set(flattened) != set(ingredient_ids):
        errors.append(f"{recipe_id}: ingredient ID/group mismatch")

    if any(not group for group in groups):
        errors.append(f"{recipe_id}: empty ingredient group")

    required_ids = {
        ingredient_id
        for group in required
        for ingredient_id in group
    }

    optional_ids = {
        ingredient_id
        for group in optional
        for ingredient_id in group
    }

    if required_ids.intersection(optional_ids):
        errors.append(f"{recipe_id}: required/optional overlap")

    if required_ids.union(optional_ids) != set(flattened):
        errors.append(f"{recipe_id}: classification mismatch")

if len(ids) != len(set(ids)):
    errors.append("Duplicate recipe IDs detected")

print(f"Total ingredient groups: {total_groups}")
print(f"Unique recipe IDs: {len(set(ids))}")

print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

print(f"Validation errors: {len(errors)}")

if errors:
    for error in errors:
        print("-", error)
else:
    print("ALL SAVED INDEX CHECKS PASSED.")

print("\nNo files modified.")
