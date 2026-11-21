
from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager


print("=" * 65)
print("RAG RETRIEVAL TEST")
print("=" * 65)

# Load saved index
retriever = RecipeRetriever(
    model_name="intfloat/multilingual-e5-small"
)

manager = RecipeIndexManager()
load_info = manager.load(retriever)

print("Index loaded:", load_info)
print("Indexed documents:", retriever.index.ntotal)


# Test queries
queries = [
    "How do I prepare Lebanese fattoush?",
    "Lebanese recipes with lentils and bulgur",
    "Recipes containing eggplant and tahini",
    "وصفات لبنانية تحتوي على العدس",
    "Recettes libanaises avec des pois chiches",
]


for query in queries:
    print("\n" + "-" * 65)
    print("QUERY:", query)
    print("-" * 65)

    results = retriever.search(query, top_k=5)

    print("Result type:", type(results).__name__)

    if isinstance(results, dict):
        print("Result keys:", list(results.keys()))

        # Display likely result collections.
        for key, value in results.items():
            if isinstance(value, list):
                print(f"\n{key}:")
                for item in value[:5]:
                    if isinstance(item, dict):
                        metadata = item.get("metadata", {})
                        print(
                            metadata.get("id"),
                            metadata.get("name_en"),
                            "Score:",
                            item.get("score")
                        )
                    else:
                        print(str(item)[:300])

    elif isinstance(results, list):
        for rank, item in enumerate(results[:5], start=1):
            print(f"\nResult {rank}:")

            if isinstance(item, dict):
                metadata = item.get("metadata", {})
                print("Recipe ID:", metadata.get("id"))
                print("Recipe:", metadata.get("name_en"))
                print("Score:", item.get("score"))

                if not metadata:
                    print("Available keys:", list(item.keys()))
                    print("Preview:", str(item)[:500])
            else:
                print(str(item)[:500])

    else:
        print("Returned value:", str(results)[:1500])


print("\n" + "=" * 65)
print("RETRIEVAL TEST COMPLETED")
print("=" * 65)
