
from src.recipe.recipe_loader import RecipeLoader
from src.rag.recipe_retriever import RecipeRetriever


loader = RecipeLoader()
recipes = loader.load_recipes()

retriever = RecipeRetriever()

shape = retriever.index_recipes(recipes)

print("Embedding shape:", shape)

query = "I have bulgur, ground beef, onion and pine nuts"

results = retriever.retrieve(query, top_k=3)

print("\nRetrieved recipes:")

for result in results:
    recipe = result["recipe"]

    print("\nName:", recipe["name"])
    print("Similarity:", round(result["score"], 4))
