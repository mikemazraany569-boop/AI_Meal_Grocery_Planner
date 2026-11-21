
from src.rag.recipe_document_builder import RecipeDocumentBuilder
from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent

# Load the actual Lebanese recipe dataset
recipes_path = ROOT / "data" / "recipes" / "lebanese_dishes_reference.json"

with recipes_path.open("r", encoding="utf-8") as file:
    data = json.load(file)

recipes = data["dishes"]

print("Recipes loaded:", len(recipes))

# Build RAG documents
builder = RecipeDocumentBuilder()
documents = builder.build_documents(recipes)

# Verify original recipes are preserved
assert documents, "No documents were generated."

for document in documents:
    assert isinstance(document["metadata"].get("recipe"), dict)

print("Documents built:", len(documents))
print("Original recipe metadata verified.")

# Build FAISS index
retriever = RecipeRetriever()
retriever.build_index(documents)

# Save index and documents
manager = RecipeIndexManager()
manager.save(retriever)

print("\nIndex rebuilt successfully.")
print("FAISS vectors:", retriever.index.ntotal)
print("Embedding dimensions:", retriever.index.d)
