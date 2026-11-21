
from src.recipe.recipe_loader import RecipeLoader
from src.rag.recipe_document_builder import RecipeDocumentBuilder
from src.rag.recipe_retriever import RecipeRetriever

# Load recipes
loader = RecipeLoader()
recipes = loader.load_recipes()

# Build documents
builder = RecipeDocumentBuilder()
documents = builder.build_documents(recipes)

# Build retriever
retriever = RecipeRetriever()
total = retriever.build_index(documents)

print("INDEX SIZE:", total)

# Simulated fridge inventory
inventory_ids = [
    "ING011",  # eggplant
    "ING012",  # tahini
    "ING009",  # lemon
    "ING008",  # garlic
    "ING014",  # salt
    "ING007",  # olive oil
]

# Search
results = retriever.search(
    query="Lebanese dishes I can prepare with my ingredients",
    top_k=5,
    ingredient_ids=inventory_ids
)

print("\nINVENTORY-BASED RECIPE RESULTS")
print("=" * 60)

for result in results:
    metadata = result["metadata"]

    print(f"\n{metadata['id']} - {metadata['name_en']}")
    print("Combined score:", round(result["score"], 4))
    print("Semantic score:", round(result["semantic_score"], 4))
    print("Required coverage:", round(result["ingredient_coverage"] * 100, 2), "%")
    print("Optional coverage:", round(result["optional_ingredient_coverage"] * 100, 2), "%")
    print(
        "Matched required ingredients:",
        result["matched_required_ingredients"],
        "/",
        result["total_required_ingredients"]
    )
    print("Missing required groups:", result["missing_required_groups"])
