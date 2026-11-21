
import json
import shutil
from datetime import datetime
from pathlib import Path

from src.rag.recipe_document_builder import RecipeDocumentBuilder
from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent

RECIPE_FILE = (
    ROOT / "data" / "recipes" / "lebanese_recipes_enriched.json"
)

INGREDIENT_FILE = (
    ROOT / "data" / "ingredients" / "ingredients_multilingual.json"
)

INDEX_FILE = ROOT / "data" / "vector_store" / "recipes.index"
DOCUMENTS_FILE = ROOT / "data" / "vector_store" / "recipes.json"

EXPECTED_RECIPE_COUNT = 50


# --------------------------------------------------
# STEP 1 — LOAD SOURCE DATA
# --------------------------------------------------

print("=" * 65)
print("RAG INDEX REBUILD")
print("=" * 65)

with RECIPE_FILE.open("r", encoding="utf-8") as file:
    recipe_data = json.load(file)

if isinstance(recipe_data, list):
    recipes = recipe_data
elif isinstance(recipe_data, dict):
    recipes = recipe_data.get("recipes")

    if not isinstance(recipes, list):
        recipes = recipe_data.get("dishes")

    if not isinstance(recipes, list):
        raise ValueError("Could not find the recipe list in the JSON.")
else:
    raise TypeError("Unexpected recipe JSON structure.")

if len(recipes) != EXPECTED_RECIPE_COUNT:
    raise ValueError(
        f"Expected {EXPECTED_RECIPE_COUNT} recipes, found {len(recipes)}."
    )

if not all(isinstance(recipe, dict) for recipe in recipes):
    raise TypeError("A recipe record is not a dictionary.")

recipe_ids = [recipe.get("id") for recipe in recipes]

if len(recipe_ids) != len(set(recipe_ids)):
    raise ValueError("Duplicate recipe IDs detected.")

print("Recipes loaded:", len(recipes))


# --------------------------------------------------
# STEP 2 — BUILD DOCUMENTS
# --------------------------------------------------

builder = RecipeDocumentBuilder(INGREDIENT_FILE)

documents = builder.build_documents(recipes)

if len(documents) != len(recipes):
    raise ValueError("Document count does not match recipe count.")

document_ids = [
    document["metadata"]["id"]
    for document in documents
]

if len(document_ids) != len(set(document_ids)):
    raise ValueError("Duplicate document IDs detected.")

# Validate original recipe metadata.
for document in documents:
    metadata = document.get("metadata", {})
    original_recipe = metadata.get("recipe")

    if not isinstance(original_recipe, dict):
        raise ValueError(
            f"Missing original recipe metadata: {metadata.get('id')}"
        )

# Validate all detailed ingredient IDs.
missing_detailed_ids = []

for document in documents:
    metadata = document["metadata"]
    original_recipe = metadata["recipe"]

    document_ingredient_ids = set(metadata["ingredient_ids"])

    for item in original_recipe.get("ingredients_detailed", []):
        ingredient_id = item.get("ingredient_id")

        if ingredient_id and ingredient_id not in document_ingredient_ids:
            missing_detailed_ids.append(
                (metadata["id"], item.get("name"), ingredient_id)
            )

if missing_detailed_ids:
    raise ValueError(
        f"Detailed ingredient IDs missing: {missing_detailed_ids}"
    )

# Validate ingredient IDs against the dictionary.
valid_ingredient_ids = set(builder.ingredients)

invalid_ids = []

for document in documents:
    for ingredient_id in document["metadata"]["ingredient_ids"]:
        if ingredient_id not in valid_ingredient_ids:
            invalid_ids.append(
                (document["metadata"]["id"], ingredient_id)
            )

if invalid_ids:
    raise ValueError(f"Invalid ingredient IDs: {invalid_ids}")

print("Documents built:", len(documents))
print("Unique document IDs:", len(set(document_ids)))
print("Detailed ingredient ID validation: PASSED")
print("Ingredient dictionary validation: PASSED")
print("Original recipe metadata: PRESERVED")


# --------------------------------------------------
# STEP 3 — LOAD LOCAL EMBEDDING MODEL
# --------------------------------------------------

print("\nLoading local embedding model...")

retriever = RecipeRetriever(
    model_name="intfloat/multilingual-e5-small"
)

print("Embedding model loaded.")


# --------------------------------------------------
# STEP 4 — BUILD FAISS INDEX IN MEMORY
# --------------------------------------------------

print("\nBuilding FAISS index...")

index_size = retriever.build_index(documents)

if index_size != EXPECTED_RECIPE_COUNT:
    raise ValueError(
        f"Expected {EXPECTED_RECIPE_COUNT} vectors, got {index_size}."
    )

if retriever.index.ntotal != len(documents):
    raise ValueError("FAISS vector count does not match document count.")

print("FAISS vectors built:", index_size)
print("Embedding dimensions:", retriever.index.d)


# --------------------------------------------------
# STEP 5 — BACK UP EXISTING VECTOR STORE
# --------------------------------------------------

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

backup_files = []

for file_path in (INDEX_FILE, DOCUMENTS_FILE):
    if file_path.exists():
        backup_path = file_path.with_name(
            f"{file_path.stem}.backup_{timestamp}{file_path.suffix}"
        )

        shutil.copy2(file_path, backup_path)
        backup_files.append(backup_path)

print("\nExisting vector-store backups:")

if backup_files:
    for backup in backup_files:
        print(" -", backup.name)
else:
    print("No previous vector-store files existed.")


# --------------------------------------------------
# STEP 6 — SAVE NEW VECTOR STORE
# --------------------------------------------------

manager = RecipeIndexManager(
    index_path=str(INDEX_FILE),
    documents_path=str(DOCUMENTS_FILE)
)

manager.save(retriever)

if not INDEX_FILE.exists() or not DOCUMENTS_FILE.exists():
    raise RuntimeError("Vector-store files were not created.")

print("\n" + "=" * 65)
print("RAG INDEX REBUILD COMPLETED")
print("=" * 65)

print("Recipes indexed:", retriever.index.ntotal)
print("Documents saved:", len(retriever.documents))
print("Index file:", INDEX_FILE)
print("Documents file:", DOCUMENTS_FILE)

print("\nBackups created:", len(backup_files))
