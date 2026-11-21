
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent

RECIPE_FILE = (
    ROOT / "data" / "recipes"
    / "lebanese_recipes_enriched.json"
)

BACKUP_FILE = RECIPE_FILE.with_name(
    "lebanese_recipes_enriched_before_batch4.json"
)

RECIPES = [
    {
        "id": "LB046",
        "name_en": "Freekeh with Chicken",
        "source_display_name": "Freekeh bi Djej",
        "name_ar": "فريكة بالدجاج",
        "category": "main_dish",
        "servings": 6,
        "preparation_time_minutes": 45,
        "cooking_time_minutes": 60,
        "total_time_minutes": 105,
        "time_notes": "Water quantity is specified by the cooking method, not measured in the ingredient list.",
        "ingredients": [
            ("chicken breast", 800, "g", False),
            ("freekeh", 600, "g", False),
            ("onions", 5, "pieces", False),
            ("olive oil", 4, "tablespoons", False),
            ("salt", None, None, False),
            ("black pepper", None, None, False),
            ("water", None, None, False),
        ],
        "instructions": [
            "Wash the freekeh thoroughly several times to remove sand and impurities. Do not soak it, to preserve its smoky flavor.",
            "Cut the chicken breasts into large pieces.",
            "Heat two tablespoons of olive oil and sauté the chicken for about five minutes until lightly browned.",
            "Finely chop the onions and sauté them in the remaining two tablespoons of olive oil for about ten minutes without browning.",
            "Add the freekeh and chicken to the onions. Season with salt and black pepper.",
            "Add enough water to cover the freekeh by approximately two finger widths. Bring to a boil, then cook over low heat for about 40 minutes until the chicken and freekeh are cooked and creamy.",
            "Serve hot."
        ],
        "source": [
            "https://today.lorientlejour.com/cooking-food-lebanon/1485648/"
        ],
        "notes": [
            "Adapted from the recipe attributed to Kamal Mouzawak's book Manger libanais.",
            "The source gives no exact water quantity. The method specifies covering the freekeh by two finger widths.",
            "Salt and black pepper quantities are unspecified in the source."
        ],
    },
    {
        "id": "LB047",
        "name_en": "Lebanese Peas and Carrots Stew",
        "source_display_name": "Yakhnet Bazella w Jazar",
        "name_ar": "يخنة البازيلاء والجزر",
        "category": "main_dish",
        "servings": 6,
        "preparation_time_minutes": 15,
        "cooking_time_minutes": 60,
        "total_time_minutes": 75,
        "time_notes": "Source cooking time is approximately one hour.",
        "ingredients": [
            ("sunflower oil", 50, "ml", False),
            ("medium onions", 2, "pieces", False),
            ("small garlic cloves", 10, "pieces", False),
            ("lamb leg or shoulder meat", 500, "g", False),
            ("cinnamon", 1, "teaspoon", False),
            ("hot water", 0.5, "litre", False),
            ("frozen peas", 500, "g", False),
            ("carrots", 250, "g", False),
            ("tomato sauce", 500, "ml", False),
            ("salt", 1.5, "teaspoons", False),
            ("black pepper", 0.25, "teaspoon", False),
            ("allspice", 0.25, "teaspoon", False),
            ("curry powder", 2, "teaspoons", False),
            ("tomato paste", 2, "heaped tablespoons", False),
        ],
        "instructions": [
            "Heat the sunflower oil in a pressure cooker over medium-high heat. Sauté the chopped onions and sliced garlic for about five minutes until softened and golden.",
            "Add the lamb cubes and cinnamon. Brown the meat for approximately five to ten minutes, stirring regularly.",
            "Add the hot water, close the pressure cooker, and cook according to its manufacturer's instructions over medium-low heat for about twenty minutes.",
            "In a separate large pot, combine the frozen peas, carrots, tomato sauce, tomato paste, salt, black pepper, allspice and curry powder.",
            "Carefully open the pressure cooker and transfer the meat together with its cooking liquid into the vegetable pot.",
            "Bring to a boil, then reduce the heat, cover and cook for about twenty minutes until the vegetables are tender.",
            "Remove the lid and simmer for approximately ten more minutes until the sauce thickens slightly.",
            "Serve hot, traditionally with rice."
        ],
        "source": [
            "https://dinas-kitchen.com/2025/10/24/yachnet-bazella-w-jazzar-lamb-stew-with-peas-and-carrots/"
        ],
        "notes": [
            "The source uses lamb from the leg or shoulder.",
            "The source describes pressure-cooker preparation for the meat.",
            "The recipe is also described as adaptable to beef."
        ],
    },
    {
        "id": "LB048",
        "name_en": "Lebanese Spinach Stew",
        "source_display_name": "Yakhnet Sbanekh",
        "name_ar": "يخنة السبانخ",
        "category": "main_dish",
        "servings": 4,
        "preparation_time_minutes": 20,
        "cooking_time_minutes": 35,
        "total_time_minutes": 55,
        "time_notes": "Source provides fresh and frozen spinach options.",
        "ingredients": [
            ("fresh spinach or frozen leaf spinach", None, None, False),
            ("olive oil", 3, "tablespoons", False),
            ("pine nuts", 40, "g", False),
            ("large onion", 1, "piece", False),
            ("ground beef or lamb", 400, "g", False),
            ("seven spices", 1.5, "teaspoons", False),
            ("black pepper", 0.5, "teaspoon", False),
            ("salt", 1.25, "teaspoons", False),
            ("chicken or vegetable stock or water", 750, "ml", False),
            ("garlic cloves", 6, "pieces", False),
            ("fresh coriander", 1, "bunch", False),
            ("lemon juice", 1.5, "lemons", False),
            ("chili flakes", None, None, True),
        ],
        "instructions": [
            "If using fresh spinach, remove thick stems, wash the leaves thoroughly and roughly chop them. If using frozen spinach, thaw it and squeeze out some excess water.",
            "Heat one tablespoon of olive oil in a heavy pot over medium-low heat. Toast the pine nuts for three to four minutes until golden, then remove and set aside.",
            "Add another tablespoon of olive oil. Cook the chopped onion with a pinch of salt for six to eight minutes until soft and lightly golden.",
            "Add the ground meat and cook for five to six minutes, breaking it apart, until browned. Stir in the seven spices, black pepper and one teaspoon of salt.",
            "Add the spinach gradually, stirring until each batch wilts.",
            "Pour in the stock or water. Bring to a boil, then simmer uncovered for twelve to fifteen minutes until the spinach is tender.",
            "In a separate pan, heat the remaining olive oil. Cook the crushed garlic for about one minute, then add the chopped coriander and optional chili flakes. Stir until fragrant.",
            "Stir the garlic and coriander mixture and lemon juice into the stew. Simmer for another three minutes and adjust the seasoning.",
            "Serve hot with vermicelli rice and toasted pine nuts."
        ],
        "source": [
            "https://www.madeinliban.com/how-to-make-lebanese-spinach-stew/"
        ],
        "notes": [
            "The source specifies 1 kg fresh spinach or 600 g frozen leaf spinach.",
            "Ground beef or lamb is an alternative.",
            "Chicken stock, vegetable stock or water are alternatives.",
            "Chili flakes are optional.",
            "The source describes serving the stew with vermicelli rice."
        ],
    },
    {
        "id": "LB049",
        "name_en": "Lebanese Lentil Soup",
        "source_display_name": "Shorbet Adas",
        "name_ar": "شوربة العدس",
        "category": "soup",
        "servings": 8,
        "preparation_time_minutes": 10,
        "cooking_time_minutes": 60,
        "total_time_minutes": 70,
        "time_notes": "Source gives 12 cups of water or broth.",
        "ingredients": [
            ("lentils", 2.5, "cups", False),
            ("medium onion", 1, "piece", False),
            ("large carrot", 1, "piece", False),
            ("small potato", 1, "piece", False),
            ("cumin powder", 2, "teaspoons", False),
            ("black pepper", 1, "teaspoon", False),
            ("salt", 1, "tablespoon", False),
            ("water or broth", 12, "cups", False),
            ("fresh parsley", 2, "tablespoons", False),
            ("lemon juice", 3, "lemons", False),
            ("fried or toasted pita bread", None, None, True),
            ("caramelized onions", None, None, True),
        ],
        "instructions": [
            "Wash the lentils thoroughly. Place them in a large pot with the chopped onion, carrot and potato.",
            "Add the water or broth, approximately twelve cups, and bring to a boil.",
            "Reduce the heat and simmer for about one hour, until the lentils and vegetables are very soft.",
            "Turn off the heat and allow the soup to rest for approximately ten minutes.",
            "Remove and reserve some excess liquid if necessary. Blend the soup until smooth and creamy. Allow it to cool slightly first if using a regular blender.",
            "Return the soup to the pot. Add the salt, parsley and cumin, along with any reserved liquid. Bring to a boil and simmer for ten to fifteen minutes, stirring occasionally.",
            "Remove from the heat and stir in the lemon juice. Serve with optional fried or toasted pita bread and caramelized onions."
        ],
        "source": [
            "https://middlebury.coop/recipe/shorbet-adas-lebanese-lentil-soup/"
        ],
        "notes": [
            "The source describes red lentils as the traditional choice but permits green or brown lentils with a longer cooking time.",
            "Water or broth may be used.",
            "Fried or toasted pita bread and caramelized onions are optional garnishes.",
            "The source attributes the recipe to Mariam Ezzeddine of cookinwithmima.com."
        ],
    },
    {
        "id": "LB050",
        "name_en": "Lebanese Rice Pudding",
        "source_display_name": "Riz bi Haleeb",
        "name_ar": "رز بحليب",
        "category": "dessert",
        "servings": 5,
        "preparation_time_minutes": None,
        "cooking_time_minutes": None,
        "total_time_minutes": None,
        "time_notes": "The source does not provide preparation or cooking times. Makes approximately five small bowls.",
        "ingredients": [
            ("medium-grain rice", 0.5, "cup", False),
            ("water", 1, "cup", False),
            ("full-cream milk", 5, "cups", False),
            ("white granulated sugar", 0.5, "cup", False),
            ("corn flour or cornstarch", 1.5, "tablespoons", False),
            ("rose water", 1.5, "tablespoons", False),
            ("orange blossom water", 1.5, "tablespoons", False),
            ("cinnamon or chopped pistachios", None, None, True),
        ],
        "instructions": [
            "Combine the rice and water in a pot. Cook over low to medium heat for approximately five minutes.",
            "When the rice has started softening but is not fully cooked, add the milk, sugar and cornstarch. Stir well.",
            "Continue cooking over low to medium heat for approximately fifteen minutes, stirring until the rice is fully cooked and softened.",
            "Add the rose water and orange blossom water. Stir to combine.",
            "If necessary, add approximately half a cup of additional milk to maintain a creamy consistency.",
            "Simmer for another two to three minutes, stirring occasionally.",
            "Transfer into small serving bowls. Garnish with cinnamon or chopped pistachios. Serve warm or refrigerate and serve cold."
        ],
        "source": [
            "https://wlcunsw.org.au/articles/recipe-riz-bi-haleeb-lebanese-rice-pudding/"
        ],
        "notes": [
            "The source specifies medium-grain Jasmine rice.",
            "Cinnamon or chopped pistachios are optional garnishes.",
            "The source states approximately five small bowls.",
            "The source does not provide preparation or cooking times.",
            "The source lists 1.5 tablespoons (30 ml) of corn flour; preserve the source quantity as written."
        ],
    },
]


def make_recipe(record):
    detailed = []
    normalized = []

    for name, quantity, unit, optional in record["ingredients"]:
        detailed.append({
            "name": name,
            "quantity": quantity,
            "unit": unit,
            "optional": optional,
            "ingredient_id": None,
            "canonical_name": None,
        })

        normalized.append({
            "original": name,
            "status": "needs_review",
            "components": [],
            "alternatives": [],
        })

    return {
        "id": record["id"],
        "name_en": record["name_en"],
        "source_display_name": record["source_display_name"],
        "name_ar": record["name_ar"],
        "category": record["category"],
        "servings": record["servings"],
        "preparation_time_minutes": record["preparation_time_minutes"],
        "cooking_time_minutes": record["cooking_time_minutes"],
        "total_time_minutes": record["total_time_minutes"],
        "time_notes": record["time_notes"],
        "ingredients_original": [
            item[0] for item in record["ingredients"]
        ],
        "ingredients_detailed": detailed,
        "ingredients_normalized": normalized,
        "instructions": [
            {"step": index, "text_en": text}
            for index, text in enumerate(record["instructions"], 1)
        ],
        "source": record["source"],
        "verification_status": "instructions_reconstructed_source_not_original",
        "notes": record["notes"],
    }


# Load existing dataset
with open(RECIPE_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

recipes = data["recipes"]

existing_ids = {recipe["id"] for recipe in recipes}
new_ids = {recipe["id"] for recipe in RECIPES}

# Validate before changing anything
if len(new_ids) != len(RECIPES):
    raise ValueError("Duplicate IDs inside Batch 4.")

conflicts = existing_ids & new_ids

if conflicts:
    raise ValueError(
        "No changes made. These IDs already exist: "
        + ", ".join(sorted(conflicts))
    )

if len(recipes) != 45:
    raise ValueError(
        f"Expected 45 existing recipes, found {len(recipes)}. "
        "Check the active dataset before inserting."
    )

if BACKUP_FILE.exists():
    raise FileExistsError(
        f"Backup already exists: {BACKUP_FILE}"
    )

# Create backup
shutil.copy2(RECIPE_FILE, BACKUP_FILE)

# Insert new recipes
for record in RECIPES:
    recipes.append(make_recipe(record))

# Save dataset
with open(RECIPE_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 65)
print("BATCH 4 INSERTION COMPLETED")
print("=" * 65)

for record in RECIPES:
    print(
        f"{record['id']} - {record['name_en']} | "
        f"Ingredients: {len(record['ingredients'])} | "
        f"Instructions: {len(record['instructions'])}"
    )

print(f"\nTotal recipes: {len(recipes)}")
print(f"Backup: {BACKUP_FILE.name}")
print("\nAll new ingredients are awaiting normalization.")
