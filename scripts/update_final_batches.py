
import json
import shutil
from pathlib import Path


# --------------------------------------------------
# PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RECIPE_FILE = (
    PROJECT_ROOT / "data" / "recipes"
    / "lebanese_recipes_enriched.json"
)

BACKUP_FILE = (
    PROJECT_ROOT / "data" / "recipes"
    / "lebanese_recipes_enriched_before_final_instructions.json"
)


# --------------------------------------------------
# RECONSTRUCTED INSTRUCTIONS
# --------------------------------------------------

INSTRUCTIONS = {

    "LB020": [
        "Wash the eggplant and cut it into slices or chunks.",
        "Arrange the eggplant on a baking tray, coat lightly with olive oil, and roast until softened and lightly browned.",
        "Dice the onion and mince the garlic.",
        "Heat olive oil in a pot and cook the onion until softened.",
        "Add the garlic and cook briefly.",
        "Add the chickpeas, diced tomatoes, tomato paste, and the listed spicy mint blend.",
        "Season with salt and pepper.",
        "Add the roasted eggplant and stir gently.",
        "Simmer until the sauce thickens and the flavors combine.",
        "Serve warm with pita chips or crusty bread."
    ],

    "LB021": [
        "Place the chicken in a pot with water, carrot, onion, whole peppercorns, cardamom, cinnamon, and cloves.",
        "Add salt and simmer until the chicken is fully cooked.",
        "Remove the chicken and strain the broth, reserving it for the rice.",
        "Remove the chicken meat from the bones if using bone-in chicken, and set aside.",
        "Rinse the basmati rice until the water runs mostly clear.",
        "Heat vegetable oil in a pot and add the cumin.",
        "Add the rice and stir briefly.",
        "Add the reserved chicken broth and tomato juice.",
        "Cook until the rice is tender and the liquid is absorbed.",
        "Serve the rice with the cooked chicken."
    ],

    "LB022": [
        "Cut the meat into manageable pieces.",
        "Place it in a pot with water, carrot, onion, whole peppercorns, cardamom, cinnamon, and cloves.",
        "Add salt and simmer until the meat is tender.",
        "Remove the meat and strain the broth, reserving it for the rice.",
        "Rinse the basmati rice until the water runs mostly clear.",
        "Heat vegetable oil in a pot and add the cumin.",
        "Add the rice and stir briefly.",
        "Add the reserved meat broth and tomato juice.",
        "Cook until the rice is tender and the liquid is absorbed.",
        "Serve the rice with the cooked meat."
    ],

    "LB023": [
        "Clean the sea bass and pat it dry. If using fillets, check for remaining bones.",
        "Season the fish with salt and lemon juice.",
        "Slice the onions and cook them in vegetable oil until deeply browned.",
        "Remove the onions and reserve them.",
        "Season the fish with salt and the listed cumin and caraway.",
        "Coat the fish lightly with flour.",
        "Heat vegetable oil and cook the fish until fully cooked and browned. Set aside.",
        "Add the reserved onions to a pot with the rice.",
        "Add fish stock and cook until the rice is tender and the liquid is absorbed.",
        "Melt the butter and use it to finish the rice if desired.",
        "Toast the pine nuts until golden.",
        "Serve the rice with the fish, toasted pine nuts, and lemon juice."
    ],

    "LB024": [
        "Slice the chicken into thin, even strips.",
        "Slice the onions and mince the garlic.",
        "Combine olive oil, red vinegar, lemon juice, pepper, cinnamon, nutmeg, salt, and garlic.",
        "Add the chicken and onions to the marinade.",
        "Mix thoroughly, cover, and refrigerate to allow the flavors to develop.",
        "Heat a pan over medium-high heat.",
        "Cook the chicken and onions, turning regularly, until the chicken is fully cooked and lightly browned.",
        "Serve hot."
    ],

    "LB025": [
        "Slice the meat into thin strips.",
        "Slice the onions and mince the garlic.",
        "Combine olive oil, red vinegar, lemon juice, pepper, cinnamon, nutmeg, salt, and garlic.",
        "Add the meat and onions to the marinade.",
        "Mix thoroughly, cover, and refrigerate to allow the flavors to develop.",
        "Heat a pan over medium-high heat.",
        "Cook the meat and onions, stirring regularly, until the meat is thoroughly cooked and browned.",
        "Serve hot."
    ],

    "LB027": [
        "Rinse the vine leaves. If preserved in brine, rinse them thoroughly to remove excess salt.",
        "Rinse the rice and drain it.",
        "Finely chop the tomatoes, onion, parsley, and mint.",
        "Combine the rice, meat, tomatoes, onion, parsley, mint, olive oil, lemon juice, and salt.",
        "Place a vine leaf flat with its veined side facing upward.",
        "Add a small amount of filling near the base of the leaf.",
        "Fold in the sides and roll tightly, leaving room for the rice to expand.",
        "Repeat with the remaining leaves and filling.",
        "Arrange the rolls tightly in a cooking pot.",
        "Add water and additional lemon juice from the listed ingredients.",
        "Place a heatproof plate over the rolls to keep them in place.",
        "Cover and simmer until the rice and meat are fully cooked and the leaves are tender.",
        "Allow the rolls to rest briefly before serving."
    ],

    "LB028": [
        "Wash the okra and trim the stems carefully without cutting into the pods.",
        "Cut the lamb into cubes and chop the onions.",
        "Heat a pot and cook the lamb until lightly browned.",
        "Add the onions and cook until softened.",
        "Add the minced garlic and chopped tomatoes.",
        "Add water and bring the mixture to a gentle boil.",
        "Reduce the heat and simmer until the lamb begins to become tender.",
        "Add the okra, salt, and pepper.",
        "Continue simmering until the okra is tender and the lamb is fully cooked.",
        "Add the chopped green coriander and lemon juice.",
        "Simmer briefly and serve."
    ],

    "LB029": [
        "Rinse the white beans and soak them in water until softened.",
        "Cut the lamb shoulder into pieces and chop the onions.",
        "Heat olive oil in a pot and brown the lamb.",
        "Add the onions and cook until softened.",
        "Add the garlic and coriander.",
        "Add the tomato juice and stir.",
        "Add the soaked beans and the listed water or chicken stock.",
        "Season with salt and black pepper.",
        "Bring to a boil, then reduce the heat.",
        "Cover and simmer until the lamb and beans are fully tender.",
        "Check the liquid during cooking and add more water if needed.",
        "Serve warm."
    ],

    "LB030": [
        "Clean and prepare the chicken.",
        "Place it in a pot with water, onion, and salt.",
        "Simmer until the chicken is fully cooked.",
        "Remove the chicken and strain the broth, reserving it.",
        "Prepare the molokhia according to its form: wash and chop fresh leaves, or prepare dried leaves as appropriate.",
        "Add the molokhia to the reserved chicken broth.",
        "Simmer gently until the molokhia is cooked.",
        "Chop the garlic, coriander, and shallots.",
        "Heat vegetable oil in a pan and sauté the shallots until softened.",
        "Add the garlic and coriander and cook briefly until fragrant.",
        "Stir this garlic-coriander mixture into the molokhia.",
        "Add lemon juice and vinegar, adjusting according to the recipe's taste.",
        "Cook the basmati rice separately until tender.",
        "Cut the pita bread into pieces and toast or fry until crisp.",
        "Serve the molokhia with the chicken, rice, and pita bread."
    ]
}


# --------------------------------------------------
# NOTES
# --------------------------------------------------

NOTES = {
    "LB020": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The branded Piquant Post Spicy Mint blend is retained as listed; "
        "its composition has not been inferred."
    ),

    "LB021": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original reference does not provide these steps or quantities."
    ),

    "LB022": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The source specifies medium fat meat without identifying the "
        "animal or cut. This uncertainty is preserved."
    ),

    "LB023": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The original reference does not provide these steps or quantities."
    ),

    "LB024": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The source specifies pepper without identifying its variety."
    ),

    "LB025": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The source specifies meat without identifying its animal type "
        "or cut, and specifies pepper without identifying its variety."
    ),

    "LB027": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The source specifies meat without identifying its animal type "
        "or cut."
    ),

    "LB028": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The source does not provide quantities or cooking times."
    ),

    "LB029": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The source gives water or chicken stock as alternatives; "
        "both options are preserved."
    ),

    "LB030": (
        "Cooking instructions reconstructed from the listed ingredients. "
        "The source does not specify whether the molokhia is fresh or dried."
    )
}


# --------------------------------------------------
# VALIDATE FILE AND DATA
# --------------------------------------------------

if not RECIPE_FILE.exists():
    raise FileNotFoundError(f"Recipe file not found: {RECIPE_FILE}")

with open(RECIPE_FILE, "r", encoding="utf-8") as file:
    data = json.load(file)

if not isinstance(data.get("recipes"), list):
    raise ValueError("Expected a JSON object containing a recipes list.")

recipes_by_id = {
    recipe["id"]: recipe
    for recipe in data["recipes"]
}

missing_ids = set(INSTRUCTIONS) - set(recipes_by_id)

if missing_ids:
    raise ValueError(f"Missing recipe IDs: {sorted(missing_ids)}")

already_completed = [
    recipe_id
    for recipe_id in INSTRUCTIONS
    if recipes_by_id[recipe_id].get("instructions")
]

if already_completed:
    raise RuntimeError(
        "No changes made. These recipes already have instructions: "
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
# UPDATE ONLY THE TARGET RECIPES
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

completed = sum(
    bool(recipe.get("instructions"))
    for recipe in data["recipes"]
)

print("\nFINAL INSTRUCTION BATCH UPDATED")
print("=" * 55)

for recipe_id, steps in INSTRUCTIONS.items():
    print(
        f"{recipe_id} - {recipes_by_id[recipe_id]['name_en']}: "
        f"{len(steps)} steps"
    )

print("\nRecipes with instructions:", completed, "/", len(data["recipes"]))
print("Backup:", BACKUP_FILE)
print("Recipe file updated successfully.")
