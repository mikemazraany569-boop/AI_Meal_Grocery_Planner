
from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager


def main():
    retriever = RecipeRetriever()
    manager = RecipeIndexManager()

    print("LOADING SAVED INDEX")
    print(manager.load(retriever))

    inventory_ids = [
        "ING011",
        "ING012",
        "ING009",
        "ING008",
        "ING014",
        "ING007"
    ]

    print("\nSEARCHING SAVED INDEX")

    results = retriever.search(
        query="Lebanese recipes I can prepare with my ingredients",
        top_k=5,
        ingredient_ids=inventory_ids
    )

    for result in results:
        metadata = result["metadata"]

        print(f"\n{metadata['id']} - {metadata['name_en']}")
        print(f"Score: {result['score']:.4f}")
        print(
            f"Required coverage: "
            f"{result['ingredient_coverage']:.2%}"
        )
        print(
            f"Missing groups: "
            f"{result['missing_required_groups']}"
        )

    print("\nSAVED INDEX SEARCH COMPLETED")


if __name__ == "__main__":
    main()
