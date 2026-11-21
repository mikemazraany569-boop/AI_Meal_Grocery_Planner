
import json
from pathlib import Path
from copy import deepcopy

RECIPE_PATH = Path("data/recipes/lebanese_recipes_enriched.json")
INGREDIENT_PATH = Path("data/ingredients/ingredients_multilingual.json")
BACKUP_PATH = Path(
    "data/recipes/lebanese_recipes_enriched_before_batch4_normalization.json"
)

BATCH_IDS = {f"LB{i:03d}" for i in range(46, 51)}

# Direct matches: original ingredient name -> canonical ID
DIRECT = {
    "LB046": {
        "chicken breast": "ING057",
        "freekeh": "ING092",
        "onions": "ING002",
        "olive oil": "ING007",
        "salt": "ING014",
        "black pepper": "ING015",
        "water": "ING020",
    },
    "LB047": {
        "sunflower oil": "ING072",
        "medium onions": "ING002",
        "small garlic cloves": "ING008",
        "lamb leg or shoulder meat": "ING023",
        "cinnamon": "ING048",
        "hot water": "ING020",
        "frozen peas": "ING093",
        "carrots": "ING046",
        "tomato sauce": "ING094",
        "salt": "ING014",
        "black pepper": "ING015",
        "allspice": "ING052",
        "curry powder": "ING095",
        "tomato paste": "ING056",
    },
    "LB048": {
        "fresh spinach or frozen leaf spinach": "ING032",
        "olive oil": "ING007",
        "pine nuts": "ING017",
        "large onion": "ING002",
        "seven spices": "ING074",
        "black pepper": "ING015",
        "salt": "ING014",
        "garlic cloves": "ING008",
        "fresh coriander": "ING030",
        "lemon juice": "ING009",
        "chili flakes": "ING096",
    },
    "LB049": {
        "lentils": "ING005",
        "medium onion": "ING002",
        "large carrot": "ING046",
        "small potato": "ING040",
        "cumin powder": "ING050",
        "black pepper": "ING015",
        "salt": "ING014",
        "fresh parsley": "ING003",
        "lemon juice": "ING009",
        "fried or toasted pita bread": "ING034",
        "caramelized onions": "ING002",
    },
    "LB050": {
        "medium-grain rice": "ING006",
        "water": "ING020",
        "full-cream milk": "ING097",
        "white granulated sugar": "ING022",
        "corn flour or cornstarch": "ING081",
        "rose water": "ING098",
        "orange blossom water": "ING099",
    },
}

# True alternatives: original name -> possible canonical ingredients.
# None means an unresolved choice; it must remain under review.
ALTERNATIVES = {
    "LB048": {
        "ground beef or lamb": [
            ("ground beef", "ING024"),
            ("ground lamb", "ING023"),
        ],
        "chicken or vegetable stock or water": [
            ("chicken stock", "ING079"),
            ("vegetable stock", None),
            ("water", "ING020"),
        ],
    },
    "LB049": {
        "water or broth": [
            ("water", "ING020"),
            ("broth", None),
        ],
    },
    "LB050": {
        "cinnamon or chopped pistachios": [
            ("cinnamon", "ING048"),
            ("chopped pistachios", "ING100"),
        ],
    },
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


recipes_data = load_json(RECIPE_PATH)
ingredients_data = load_json(INGREDIENT_PATH)

ingredients_by_id = {
    item["id"]: item for item in ingredients_data["ingredients"]
}

# Use the actual dictionary names for canonical display names.
canonical_names = {
    ingredient_id: item["names"]["en"][0]
    for ingredient_id, item in ingredients_by_id.items()
}

# Validate all referenced IDs before touching the recipe file.
all_mappings = []

for recipe_id, mappings in DIRECT.items():
    all_mappings.extend(mappings.values())

for recipe_id, mappings in ALTERNATIVES.items():
    for choices in mappings.values():
        all_mappings.extend(
            ingredient_id
            for _, ingredient_id in choices
            if ingredient_id is not None
        )

invalid_ids = sorted(set(all_mappings) - set(ingredients_by_id))

if invalid_ids:
    raise ValueError(f"Invalid ingredient IDs: {invalid_ids}")

# Work on a separate copy until all checks pass.
updated_data = deepcopy(recipes_data)

batch_recipes = [
    recipe for recipe in updated_data["recipes"]
    if recipe["id"] in BATCH_IDS
]

if {recipe["id"] for recipe in batch_recipes} != BATCH_IDS:
    raise ValueError("One or more Batch 4 recipes are missing.")

total_records = 0
matched_records = 0
alternative_records = 0
review_choices = 0

for recipe in batch_recipes:
    recipe_id = recipe["id"]

    detailed = recipe.get("ingredients_detailed", [])
    normalized = recipe.get("ingredients_normalized", [])

    if len(detailed) != len(normalized):
        raise ValueError(
            f"{recipe_id}: detailed/normalized count mismatch."
        )

    if len(detailed) != len(
        DIRECT.get(recipe_id, {})
    ) + len(ALTERNATIVES.get(recipe_id, {})):
        raise ValueError(
            f"{recipe_id}: mapping count does not match ingredients."
        )

    for detail, norm in zip(detailed, normalized):
        name = detail["name"]

        if norm["original"] != name:
            raise ValueError(
                f"{recipe_id}: original ingredient mismatch: {name}"
            )

        # Direct canonical match
        if name in DIRECT.get(recipe_id, {}):
            ingredient_id = DIRECT[recipe_id][name]
            canonical_name = canonical_names[ingredient_id]

            detail["ingredient_id"] = ingredient_id
            detail["canonical_name"] = canonical_name

            norm["components"] = [{
                "original": name,
                "id": ingredient_id,
                "canonical_name": canonical_name,
                "status": "matched",
            }]
            norm["alternatives"] = []
            norm["status"] = "matched"

            matched_records += 1

        # True source alternatives
        elif name in ALTERNATIVES.get(recipe_id, {}):
            choices = ALTERNATIVES[recipe_id][name]
            alternative_items = []

            unresolved = False

            for original, ingredient_id in choices:
                if ingredient_id is None:
                    alternative_items.append({
                        "original": original,
                        "id": None,
                        "canonical_name": None,
                        "status": "needs_review",
                    })
                    unresolved = True
                    review_choices += 1
                else:
                    alternative_items.append({
                        "original": original,
                        "id": ingredient_id,
                        "canonical_name": canonical_names[ingredient_id],
                        "status": "matched",
                    })

            # No single canonical ID represents an either/or choice.
            detail["ingredient_id"] = None
            detail["canonical_name"] = None

            norm["components"] = []
            norm["alternatives"] = alternative_items
            norm["status"] = "needs_review"

            alternative_records += 1

        else:
            raise ValueError(
                f"{recipe_id}: no mapping defined for {name}"
            )

        total_records += 1

# Preserve both source quantities for LB048 spinach.
spinach_recipe = next(
    r for r in batch_recipes if r["id"] == "LB048"
)

spinach = next(
    item for item in spinach_recipe["ingredients_detailed"]
    if item["name"] == "fresh spinach or frozen leaf spinach"
)

spinach["source_quantity_notes"] = (
    "The source specifies either 1 kg fresh spinach "
    "OR 600 g frozen leaf spinach. These are alternative "
    "forms and quantities, not cumulative quantities. "
    "The single quantity field is intentionally left empty."
)

# Final validation before backup and save.
valid_ids = set(ingredients_by_id)

for recipe in batch_recipes:
    for detail, norm in zip(
        recipe["ingredients_detailed"],
        recipe["ingredients_normalized"]
    ):
        ingredient_id = detail.get("ingredient_id")

        if ingredient_id is not None and ingredient_id not in valid_ids:
            raise ValueError(
                f"{recipe['id']}: invalid detailed ID {ingredient_id}"
            )

        for choice in norm.get("alternatives", []):
            choice_id = choice.get("id")
            if choice_id is not None and choice_id not in valid_ids:
                raise ValueError(
                    f"{recipe['id']}: invalid alternative ID {choice_id}"
                )

if total_records != 54:
    raise ValueError(f"Expected 54 records, got {total_records}")

if BACKUP_PATH.exists():
    raise FileExistsError(
        f"Backup already exists. Not overwriting: {BACKUP_PATH}"
    )

# Backup original, then save updated recipe data.
BACKUP_PATH.write_text(
    json.dumps(recipes_data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

RECIPE_PATH.write_text(
    json.dumps(updated_data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

print("=" * 65)
print("BATCH 4 NORMALIZATION COMPLETED")
print("=" * 65)

for recipe in sorted(batch_recipes, key=lambda r: r["id"]):
    matched = sum(
        1 for item in recipe["ingredients_normalized"]
        if item["status"] == "matched"
    )
    alternatives = sum(
        1 for item in recipe["ingredients_normalized"]
        if item["alternatives"]
    )
    review = sum(
        1 for item in recipe["ingredients_normalized"]
        if item["status"] == "needs_review"
    )

    print(
        f"{recipe['id']} - {recipe['name_en']} | "
        f"Matched: {matched} | "
        f"Alternatives: {alternatives} | "
        f"Review: {review}"
    )

print("\nSUMMARY")
print(f"Total ingredient records: {total_records}")
print(f"Direct matched records: {matched_records}")
print(f"Alternative records: {alternative_records}")
print(f"Unresolved alternative choices: {review_choices}")
print(f"Backup: {BACKUP_PATH.name}")
print("All ingredient references validated.")
