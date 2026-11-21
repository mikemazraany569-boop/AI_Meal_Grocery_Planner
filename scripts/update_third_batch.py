
import json
import shutil
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RECIPE_FILE = (
    PROJECT_ROOT
    / "data"
    / "recipes"
    / "lebanese_recipes_enriched.json"
)

BACKUP_FILE = (
    PROJECT_ROOT
    / "data"
    / "recipes"
    / "lebanese_recipes_enriched_before_batch3_instructions.json"
)


# --------------------------------------------------
# RECONSTRUCTED INSTRUCTIONS
# --------------------------------------------------

INSTRUCTIONS = {

    "LB015": [
        "Combine the flour, caster sugar, yeast, and salt in a mixing bowl.",
        "Add water gradually and incorporate the olive oil.",
        "Knead until a soft, smooth dough forms.",
        "Cover and leave the dough to rise until expanded.",
        "Finely chop or process the tomatoes.",
        "Combine the minced lamb with the tomatoes, pomegranate molasses, salt, and pepper.",
        "Divide the dough into portions and roll each into a thin round.",
        "Spread a thin layer of the meat mixture over each dough round, leaving a small border.",
        "Arrange on baking trays.",
        "Bake in a preheated oven until the dough is cooked and the meat topping is thoroughly cooked.",
        "Serve warm."
    ],

    "LB016": [
        "Wash and prepare the green beans, cutting them into manageable pieces if necessary.",
        "Heat the vegetable oil in a large pot.",
        "Add the sliced onions and cook until softened.",
        "Add the peeled garlic cloves and cook briefly.",
        "Add the chopped tomatoes and stir.",
        "Season with salt, red pepper, and seven spices.",
        "Add the green beans and mix until coated with the tomato mixture.",
        "Cover and cook gently until the beans become tender, stirring occasionally.",
        "Add a little water if necessary to prevent sticking.",
        "Finish with extra-virgin olive oil and serve warm or at room temperature."
    ],

    "LB017": [
        "Separate the cabbage leaves carefully.",
        "Blanch the leaves in boiling water until flexible enough to roll.",
        "Drain and allow them to cool.",
        "Prepare the basic vegetables stuffing according to its separately documented recipe or source.",
        "Place a portion of stuffing on each cabbage leaf.",
        "Fold in the sides and roll the leaf tightly.",
        "Arrange the stuffed cabbage rolls in a cooking pot.",
        "Add the tomato, lemon juice, water, cinnamon, and garlic cloves.",
        "Cover and simmer gently until the cabbage is tender and the stuffing is fully cooked.",
        "Add the dry mint toward the end of cooking.",
        "Allow the rolls to rest briefly before serving."
    ],

    "LB018": [
        "Rinse the lentils and remove any unwanted particles.",
        "Place the lentils in a pot with water and cook until they begin to soften.",
        "Rinse and drain the rice.",
        "Add the rice to the lentils.",
        "Season with salt and continue cooking gently until both the lentils and rice are tender.",
        "Add water as needed to prevent the mixture from drying before the grains are cooked.",
        "Slice the onions thinly.",
        "Heat the olive oil in a separate pan.",
        "Cook the onions slowly until deeply golden and caramelized.",
        "Stir some of the onions and their oil into the lentil-rice mixture.",
        "Serve with the remaining caramelized onions on top."
    ],

    "LB019": [
        "If using dried chickpeas, soak them in water and cook until tender. If already cooked, rinse and drain them.",
        "Heat the vegetable oil and butter in a large pot.",
        "Add the pearl onions and cook until softened and lightly golden.",
        "Add the caraway, ground cinnamon, ground cumin, salt, and black pepper.",
        "Stir briefly to release the spices' aroma.",
        "Add the cooked chickpeas and mix well.",
        "Prepare the moghrabieh pearls separately according to their package or preparation method, if the ingredient 'Dry dough' refers to dried moghrabieh pearls.",
        "Combine the prepared pearls with the chickpea and onion mixture.",
        "Add a little water or cooking liquid if needed to bring the dish together.",
        "Simmer briefly so the flavors combine.",
        "Serve warm."
    ]
}


# --------------------------------------------------
# RECIPE NOTES
# --------------------------------------------------

NOTES = {

    "LB015": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "Water is used in the dough preparation as an inferred process "
        "ingredient, but it is absent from the original ingredient list. "
        "No quantity has been assigned."
    ),

    "LB016": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original reference does not provide these steps or quantities."
    ),

    "LB017": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original ingredient entry 'basic vegetables stuffing' is "
        "preserved without inventing its individual components. "
        "Its composition requires further verification."
    ),

    "LB018": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original reference does not provide these steps or quantities. "
        "Water is used as a cooking medium and is not assigned a quantity."
    ),

    "LB019": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original ingredient 'Dry dough' is preserved. Its interpretation "
        "as dried moghrabieh pearls is contextual and has not been independently "
        "verified. The preparation method should be checked against the "
        "original source."
    )
}


# --------------------------------------------------
# VALIDATE FILE
# --------------------------------------------------

if not RECIPE_FILE.exists():
    raise FileNotFoundError(
        f"Recipe file not found: {RECIPE_FILE}"
    )

with open(RECIPE_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

if "recipes" not in data or not isinstance(data["recipes"], list):
    raise ValueError(
        "Expected a JSON object containing a 'recipes' list."
    )


# --------------------------------------------------
# INDEX RECIPES
# --------------------------------------------------

recipes_by_id = {
    recipe["id"]: recipe
    for recipe in data["recipes"]
}

missing_ids = set(INSTRUCTIONS) - set(recipes_by_id)

if missing_ids:
    raise ValueError(
        f"Recipes not found: {sorted(missing_ids)}"
    )


# --------------------------------------------------
# PREVENT OVERWRITING COMPLETED RECIPES
# --------------------------------------------------

already_completed = [
    recipe_id
    for recipe_id in INSTRUCTIONS
    if recipes_by_id[recipe_id].get("instructions")
]

if already_completed:
    raise RuntimeError(
        "These recipes already have instructions. "
        "No changes were made: "
        + ", ".join(sorted(already_completed))
    )


# --------------------------------------------------
# CREATE BACKUP
# --------------------------------------------------

if BACKUP_FILE.exists():
    raise FileExistsError(
        f"Backup already exists: {BACKUP_FILE}\n"
        "Rename or remove it manually before running again."
    )

shutil.copy2(RECIPE_FILE, BACKUP_FILE)


# --------------------------------------------------
# UPDATE RECIPES
# --------------------------------------------------

for recipe_id, steps in INSTRUCTIONS.items():

    recipe = recipes_by_id[recipe_id]

    recipe["instructions"] = [
        {
            "step": index,
            "text_en": instruction
        }
        for index, instruction in enumerate(steps, start=1)
    ]

    existing_notes = recipe.get("notes", [])

    if isinstance(existing_notes, str):
        existing_notes = [existing_notes]
    elif not isinstance(existing_notes, list):
        existing_notes = []

    existing_notes.append(NOTES[recipe_id])

    recipe["notes"] = existing_notes

    recipe["verification_status"] = (
        "instructions_reconstructed_source_not_original"
    )


# --------------------------------------------------
# SAVE DATASET
# --------------------------------------------------

with open(RECIPE_FILE, "w", encoding="utf-8") as file:
    json.dump(
        data,
        file,
        ensure_ascii=False,
        indent=2
    )


# --------------------------------------------------
# CONFIRMATION
# --------------------------------------------------

print("\nTHIRD INSTRUCTION BATCH UPDATED")
print("=" * 55)

for recipe_id, steps in INSTRUCTIONS.items():
    print(
        f"{recipe_id} - {recipes_by_id[recipe_id]['name_en']}: "
        f"{len(steps)} steps"
    )

completed = sum(
    bool(recipe.get("instructions"))
    for recipe in data["recipes"]
)

print("\nRecipes with instructions:", completed, "/", len(data["recipes"]))
print("Backup:", BACKUP_FILE)
print("Recipe file updated successfully.")
