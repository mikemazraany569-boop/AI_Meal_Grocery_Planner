from src.recipe.recipe_loader import RecipeLoader

loader = RecipeLoader()
recipes = loader.load_recipes()

print("Total recipes loaded:", len(recipes))

for recipe in recipes:
    print(recipe["recipe_id"], "-", recipe["name"])

print("Number of recipes:", len(recipes))

for recipe in recipes:
    print("\nRecipe:", recipe["name"])
    print("ID:", recipe["recipe_id"])
    print("Ingredients:", len(recipe["ingredients"]))
    print("Instructions:", len(recipe["instructions"]))
    print("Verification:", recipe["origin_verification_status"])