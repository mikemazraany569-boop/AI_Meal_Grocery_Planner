
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
    / "lebanese_recipes_enriched_before_batch2_instructions.json"
)


# --------------------------------------------------
# RECONSTRUCTED INSTRUCTIONS
# --------------------------------------------------

INSTRUCTIONS = {

    "LB009": [
        "Rinse the broad beans and soak them in water, preferably overnight.",
        "Drain the beans and place them in a pot with fresh water.",
        "Add the baking soda and cook gently until the beans become very tender. Add water as needed.",
        "Drain excess liquid if necessary, while retaining some cooking liquid.",
        "Mash some of the beans lightly, leaving others whole.",
        "Mix the minced garlic with lemon juice and salt.",
        "Combine the garlic-lemon mixture with the warm beans.",
        "Drizzle with olive oil and serve warm."
    ],

    "LB010": [
        "Trim and thoroughly wash the chicory greens.",
        "Bring a pot of water to a boil and add the chicory.",
        "Boil until the greens become tender.",
        "Drain and rinse with cool water, then squeeze out excess liquid.",
        "Chop the cooked greens into manageable pieces.",
        "Slice the onions and cook them gently in olive oil until soft and golden.",
        "Add the chicory and salt to the onions.",
        "Cook together briefly so the greens absorb the olive oil and onion flavor.",
        "Finish with lemon juice and serve warm or at room temperature."
    ],

    "LB012": [
        "Finely chop the parsley and one portion of the onions.",
        "Combine the minced lamb with parsley, chopped onion, salt, and pepper.",
        "Shape the mixture into kafta patties or an even layer in a baking dish.",
        "Slice the potatoes and fry them in vegetable oil until lightly golden. Set aside.",
        "Slice the remaining onions and red pepper.",
        "Arrange the kafta in a baking dish and add the fried potatoes, onions, and red pepper.",
        "Combine the tomato juice with olive oil, debs roman, and the listed salt and pepper.",
        "Pour the tomato mixture over the kafta and vegetables.",
        "Add the ripe tomatoes, sliced or chopped.",
        "Bake until the kafta is thoroughly cooked and the potatoes are tender.",
        "Allow the dish to rest briefly before serving."
    ],

    "LB013": [
        "Rinse the bulgur briefly and soak it in water until softened.",
        "Drain thoroughly and squeeze out excess moisture.",
        "Finely chop the onions.",
        "Divide the ground meat into two portions, as indicated by the ingredient description.",
        "Combine one portion of meat with the bulgur, salt, allspice, cumin, and some of the chopped onion.",
        "Knead the mixture until it becomes cohesive.",
        "Cook the remaining meat with the remaining onion until browned and thoroughly cooked.",
        "Season the filling with the listed salt and spices as appropriate, without adding new ingredients.",
        "Spread half of the bulgur-meat mixture in an oiled baking dish.",
        "Distribute the cooked meat filling evenly over it.",
        "Cover with the remaining bulgur-meat mixture and smooth the surface.",
        "Score the top into diamond or square portions.",
        "Bake until the kibbeh is thoroughly cooked and the surface is browned.",
        "Rest briefly before cutting and serving."
    ],

    "LB014": [
        "Wash the small courgettes and trim their ends.",
        "Carefully hollow out each courgette, keeping the outer walls intact.",
        "Rinse the rice and drain it well.",
        "Combine the minced lamb with the rice, salt, and black pepper.",
        "Add olive oil to the filling and mix until evenly combined.",
        "Stuff each courgette loosely, leaving room for the rice to expand.",
        "Arrange the stuffed courgettes in a cooking pot.",
        "Add water until the courgettes are mostly covered.",
        "Bring to a gentle boil, then reduce the heat.",
        "Simmer until the courgettes are tender and the rice and meat filling are fully cooked.",
        "Allow the dish to rest briefly before serving."
    ]
}


# --------------------------------------------------
# RECIPE NOTES
# --------------------------------------------------

NOTES = {
    "LB009": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original reference does not provide these steps or quantities."
    ),

    "LB010": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original reference does not provide these steps or quantities."
    ),

    "LB012": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The two onion entries and two salt-and-pepper entries in the "
        "original ingredient list are preserved. Their separate uses "
        "in the method are an interpretation."
    ),

    "LB013": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The divided meat is interpreted as an outer mixture and filling. "
        "The original reference does not provide these steps or quantities."
    ),

    "LB014": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "No tomato, garlic, or mint has been added because these ingredients "
        "are absent from the supplied ingredient list."
    )
}


# --------------------------------------------------
# VALIDATE FILES
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
# VALIDATE TARGET RECIPES
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
# SAVE
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

print("\nSECOND INSTRUCTION BATCH UPDATED")
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
