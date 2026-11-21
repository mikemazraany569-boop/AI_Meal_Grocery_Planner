
from src.recipe.recipe_loader import RecipeLoader
from src.rag.recipe_document_builder import RecipeDocumentBuilder
from src.rag.recipe_retriever import RecipeRetriever
from src.rag.recipe_index_manager import RecipeIndexManager


def main():
    print("LOADING RECIPES")
    loader = RecipeLoader()
    recipes = loader.load_recipes()

    print("BUILDING RECIPE DOCUMENTS")
    builder = RecipeDocumentBuilder()
    documents = builder.build_documents(recipes)

    print("BUILDING FAISS INDEX")
    retriever = RecipeRetriever()
    total = retriever.build_index(documents)

    print("\nSAVING INDEX")
    manager = RecipeIndexManager()
    save_result = manager.save(retriever)

    print(save_result)

    print("\nVERIFYING SAVED INDEX")
    load_result = manager.load(retriever)

    print(load_result)

    print("\nVERIFYING RECIPE METADATA")

    for document in retriever.documents:
        metadata = document.get("metadata", {})

        print(f"\n{metadata.get('id')} - {metadata.get('name_en')}")
        print(
            "Required groups:",
            len(metadata.get("required_ingredient_groups", []))
        )
        print(
            "Optional groups:",
            len(metadata.get("optional_ingredient_groups", []))
        )
        print(
            "Has quantity data:",
            metadata.get("has_quantity_data")
        )
        print(
            "Complete quantities:",
            metadata.get("has_complete_quantities")
        )

    print("\nINDEX REBUILD COMPLETED SUCCESSFULLY")


if __name__ == "__main__":
    main()
