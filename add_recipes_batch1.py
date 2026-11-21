
import json
import shutil
from pathlib import Path
from datetime import date


# ============================================================
# PATHS
# ============================================================

ROOT = Path(__file__).resolve().parent

RECIPE_FILE = ROOT / "data" / "recipes" / "lebanese_recipes_enriched.json"

INGREDIENT_FILE = (
    ROOT / "data" / "ingredients" / "ingredients_multilingual.json"
)

BACKUP_FILE = RECIPE_FILE.with_name(
    "lebanese_recipes_enriched_before_LB031_LB035.json"
)


# ============================================================
# LOAD DATA
# ============================================================

with open(RECIPE_FILE, "r", encoding="utf-8") as f:
    recipe_data = json.load(f)

with open(INGREDIENT_FILE, "r", encoding="utf-8") as f:
    ingredient_data = json.load(f)

recipes = recipe_data["recipes"]
ingredient_dictionary = ingredient_data["ingredients"]


# ============================================================
# BUILD INGREDIENT LOOKUP
# ============================================================

ingredient_lookup = {}

for ingredient in ingredient_dictionary:
    names = ingredient.get("names", {})

    for language, aliases in names.items():
        for alias in aliases:
            ingredient_lookup[alias.strip().lower()] = {
                "id": ingredient["id"],
                "canonical_name": names.get("en", [alias])[0]
            }


def normalize_ingredient(name):
    match = ingredient_lookup.get(name.strip().lower())

    if match:
        return {
            "original": name,
            "components": [{
                "original": name,
                "id": match["id"],
                "canonical_name": match["canonical_name"],
                "status": "matched"
            }],
            "alternatives": [],
            "status": "matched"
        }

    return {
        "original": name,
        "components": [],
        "alternatives": [],
        "status": "needs_review"
    }


def detailed_ingredient(name, optional=False):
    match = ingredient_lookup.get(name.strip().lower())

    return {
        "name": name,
        "quantity": None,
        "unit": None,
        "optional": optional,
        "ingredient_id": match["id"] if match else None,
        "canonical_name": (
            match["canonical_name"] if match else None
        )
    }


# ============================================================
# RECIPE BUILDER
# ============================================================

def build_recipe(
    recipe_id,
    name,
    category,
    ingredients,
    instructions,
    notes=None
):
    return {
        "id": recipe_id,
        "name_en": name,
        "source_display_name": name,
        "name_ar": None,
        "category": category,
        "servings": None,
        "preparation_time_minutes": None,
        "cooking_time_minutes": None,
        "total_time_minutes": None,
        "time_notes": (
            "Quantities and timings require source verification."
        ),

        "ingredients_original": ingredients,

        "ingredients_detailed": [
            detailed_ingredient(item)
            for item in ingredients
        ],

        "ingredients_normalized": [
            normalize_ingredient(item)
            for item in ingredients
        ],

        "instructions": [
            {
                "step": index,
                "text_en": instruction
            }
            for index, instruction in enumerate(instructions, 1)
        ],

        "source": [],

        "verification_status":
            "instructions_reconstructed_source_not_original",

        "notes": [
            "Cooking instructions are reconstructed and are not presented as original source instructions.",
            "Ingredient quantities and cooking times have not been independently verified.",
            "Unmatched ingredients require manual review."
        ] + (notes or [])
    }


# ============================================================
# LB031 - KIBBEH NAYYEH
# ============================================================

new_recipes = [

    build_recipe(
        "LB031",
        "Kibbeh Nayyeh",
        "mezze",
        [
            "lean raw lamb",
            "fine bulgur",
            "onion",
            "salt",
            "black pepper",
            "allspice",
            "cumin",
            "fresh mint",
            "olive oil"
        ],
        [
            "Rinse the fine bulgur briefly and allow it to absorb moisture until softened.",
            "Prepare the meat immediately before mixing, keeping it refrigerated until needed.",
            "Finely grate or process the onion.",
            "Combine the meat, softened bulgur, onion and seasonings.",
            "Knead the mixture until it becomes smooth and cohesive, adding a little cold water if necessary.",
            "Spread the mixture on a serving plate.",
            "Create shallow decorative grooves on the surface.",
            "Drizzle with olive oil and serve immediately with fresh mint and suitable accompaniments."
        ],
        [
            "Raw meat is used in this traditional preparation. Raw meat carries food-safety risks.",
            "Use meat specifically handled and prepared for raw consumption, maintain strict refrigeration and hygiene, and serve immediately.",
            "Avoid serving raw meat to pregnant people, young children, older adults and immunocompromised people.",
            "The meat type and ingredient quantities require source verification."
        ]
    ),

    # ========================================================
    # LB032 - KIBBEH MAKLIYEH
    # ========================================================

    build_recipe(
        "LB032",
        "Kibbeh Makliyeh",
        "main",
        [
            "fine bulgur",
            "lean minced beef",
            "minced lamb",
            "onion",
            "pine nuts",
            "salt",
            "black pepper",
            "allspice",
            "vegetable oil"
        ],
        [
            "Soak the fine bulgur in water until softened, then drain thoroughly.",
            "Prepare the kibbeh shell by combining bulgur, lean minced meat, onion and seasonings.",
            "Knead the shell mixture until it becomes smooth and workable.",
            "Prepare the filling by cooking the minced meat with chopped onion.",
            "Season the filling and stir in the pine nuts.",
            "Allow the filling to cool before shaping.",
            "Take a portion of the shell mixture and form a hollow oval shape.",
            "Fill the shell with the cooked meat mixture.",
            "Close the opening and shape the kibbeh into an oval with pointed ends.",
            "Repeat with the remaining mixture.",
            "Fry in hot oil until golden brown and thoroughly cooked.",
            "Drain on absorbent paper and serve hot."
        ],
        [
            "The shell and filling quantities require source verification.",
            "Frying temperature and cooking duration have not been source-verified."
        ]
    ),

    # ========================================================
    # LB033 - KIBBEH BIL LABAN
    # ========================================================

    build_recipe(
        "LB033",
        "Kibbeh bil Laban",
        "main",
        [
            "kibbeh shells",
            "minced lamb",
            "onion",
            "pine nuts",
            "plain yogurt",
            "cornstarch",
            "garlic",
            "fresh coriander",
            "salt",
            "black pepper",
            "dried mint"
        ],
        [
            "Prepare the kibbeh shell mixture using softened bulgur, meat and seasonings.",
            "Cook the minced meat with chopped onion until browned.",
            "Add the pine nuts to the filling and allow it to cool.",
            "Shape the kibbeh shells and fill them with the meat mixture.",
            "Seal each shell carefully.",
            "Cook the kibbeh separately until firm and cooked through.",
            "Whisk the yogurt with cornstarch until smooth.",
            "Transfer the yogurt mixture to a saucepan and heat gently while stirring continuously.",
            "Add crushed garlic and season with salt.",
            "Add the cooked kibbeh to the yogurt sauce.",
            "Simmer gently until the kibbeh is heated through and the sauce is creamy.",
            "Finish with coriander and dried mint prepared according to the chosen recipe."
        ],
        [
            "This recipe combines reconstructed kibbeh preparation with a yogurt sauce.",
            "The exact yogurt quantity, thickening method and cooking times require source verification."
        ]
    ),

    # ========================================================
    # LB034 - KIBBEH ARNABIEH
    # ========================================================

    build_recipe(
        "LB034",
        "Kibbeh Arnabieh",
        "main",
        [
            "kibbeh shells",
            "tahini",
            "bitter orange juice",
            "lemon juice",
            "mandarin juice",
            "orange juice",
            "chickpeas",
            "onion",
            "pine nuts",
            "salt",
            "black pepper"
        ],
        [
            "Prepare the kibbeh shells and shape them into hollow ovals.",
            "Cook the kibbeh shells until firm and set aside.",
            "Prepare the chickpeas separately until tender.",
            "Combine tahini with the citrus juices gradually, stirring until smooth.",
            "Add water as needed to obtain a pourable sauce.",
            "Cook the chopped onion until softened.",
            "Add the tahini and citrus mixture to the saucepan.",
            "Heat gently while stirring to prevent the sauce from separating.",
            "Add the cooked chickpeas.",
            "Add the prepared kibbeh shells to the sauce.",
            "Simmer gently until the flavors combine and the kibbeh is heated through.",
            "Finish with toasted pine nuts and serve."
        ],
        [
            "The citrus combination is a defining feature of this recipe.",
            "Exact citrus proportions and the method for preparing the sauce require source verification.",
            "Do not substitute ordinary orange juice for bitter orange without documenting the substitution."
        ]
    ),

    # ========================================================
    # LB035 - SAMBOUSEK LAHME
    # ========================================================

    build_recipe(
        "LB035",
        "Sambousek Lahme",
        "mezze",
        [
            "plain flour",
            "water",
            "vegetable oil",
            "salt",
            "minced beef",
            "onion",
            "pine nuts",
            "seven spices",
            "black pepper",
            "lemon juice"
        ],
        [
            "Combine the flour, salt, oil and water to prepare a soft dough.",
            "Knead the dough until smooth.",
            "Cover and allow it to rest.",
            "Cook the chopped onion in a little oil until softened.",
            "Add the minced meat and cook thoroughly.",
            "Season with seven spices, black pepper and salt.",
            "Stir in the pine nuts and allow the filling to cool.",
            "Roll the dough into a thin sheet.",
            "Cut the dough into small circles.",
            "Place a portion of filling in the center of each circle.",
            "Fold the dough over the filling to form a semicircle.",
            "Seal the edges firmly by pressing or crimping.",
            "Fry in hot oil until golden and cooked through.",
            "Drain and serve warm."
        ],
        [
            "The dough and filling quantities require source verification.",
            "The cooking method and pastry dimensions should be checked against the selected source."
        ]
    )
]


# ============================================================
# SAFETY CHECKS
# ============================================================

existing_ids = {recipe["id"] for recipe in recipes}

new_ids = [recipe["id"] for recipe in new_recipes]

if len(new_ids) != len(set(new_ids)):
    raise ValueError("Duplicate IDs in the new batch.")

duplicates = existing_ids.intersection(new_ids)

if duplicates:
    raise ValueError(
        f"These recipe IDs already exist: {sorted(duplicates)}"
    )

for recipe in new_recipes:
    if not recipe["ingredients_original"]:
        raise ValueError(f"{recipe['id']} has no ingredients.")

    if not recipe["instructions"]:
        raise ValueError(f"{recipe['id']} has no instructions.")

    for index, step in enumerate(recipe["instructions"], 1):
        if step["step"] != index:
            raise ValueError(
                f"Invalid instruction numbering in {recipe['id']}"
            )


# ============================================================
# BACKUP AND SAVE
# ============================================================

shutil.copy2(RECIPE_FILE, BACKUP_FILE)

recipes.extend(new_recipes)

with open(RECIPE_FILE, "w", encoding="utf-8") as f:
    json.dump(recipe_data, f, ensure_ascii=False, indent=4)


# ============================================================
# REPORT
# ============================================================

print("=" * 60)
print("RECIPE BATCH 1 - INSERTION REPORT")
print("=" * 60)

print("Recipes added:", len(new_recipes))
print("Total recipes:", len(recipes))
print("Backup:", BACKUP_FILE)

for recipe in new_recipes:
    matched = sum(
        item["status"] == "matched"
        for item in recipe["ingredients_normalized"]
    )

    total = len(recipe["ingredients_original"])

    print(
        f"{recipe['id']} - {recipe['name_en']}: "
        f"{matched}/{total} ingredients matched"
    )

print("=" * 60)
print("Batch inserted successfully.")
