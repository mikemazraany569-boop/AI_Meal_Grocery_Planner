
from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager


retriever = RecipeRetriever(
    model_name="intfloat/multilingual-e5-small"
)

manager = RecipeIndexManager()
manager.load(retriever)

tests = [
    {
        "name": "Lentils and bulgur",
        "query": "Lebanese recipes with lentils and bulgur",
        "ingredient_ids": ["ING005", "ING018"],
    },
    {
        "name": "Eggplant and tahini",
        "query": "Lebanese recipes with eggplant and tahini",
        "ingredient_ids": ["ING011", "ING012"],
    },
    {
        "name": "Chickpeas",
        "query": "Recettes libanaises avec des pois chiches",
        "ingredient_ids": ["ING004"],
    },
]

print("=" * 65)
print("INGREDIENT-AWARE RETRIEVAL TEST")
print("=" * 65)

for test in tests:
    print("\n" + "-" * 65)
    print("TEST:", test["name"])
    print("Query:", test["query"])
    print("Ingredient IDs:", test["ingredient_ids"])

    results = retriever.search(
        query=test["query"],
        top_k=5,
        ingredient_ids=test["ingredient_ids"],
    )

    for rank, result in enumerate(results, start=1):
        metadata = result.get("metadata", {})

        print(
            f"{rank}. {metadata.get('id')} — "
            f"{metadata.get('name_en')} | "
            f"Score: {result.get('score')}"
        )

        print(
            "   Ingredient IDs:",
            metadata.get("ingredient_ids", [])
        )

        print(
            "   Required groups:",
            metadata.get("required_ingredient_groups", [])
        )

print("\n" + "=" * 65)
print("TEST COMPLETED — NO FILES MODIFIED")
print("=" * 65)
