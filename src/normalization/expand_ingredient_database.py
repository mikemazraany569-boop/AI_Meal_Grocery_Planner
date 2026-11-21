
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

DB_PATH = (
    ROOT / "data" / "ingredients" / "ingredients_multilingual.json"
)

# Additional aliases for existing canonical ingredients.
EXISTING_ALIASES = {
    "ING001": [
        "cherry tomatoes",
        "ripe tomatoes",
        "chopped tomatoes",
        "diced tomatoes",
    ],
    "ING002": [
        "white onion",
        "white onions",
        "yellow onion",
        "yellow onions",
        "chopped onion",
        "finely chopped onion",
        "diced onion",
        "sliced onion",
    ],
    "ING003": [
        "flat-leaf parsley",
        "flat leaf parsley",
        "Italian parsley",
    ],
    "ING004": [
        "garbanzo beans",
        "chick pea",
        "chick peas",
    ],
    "ING005": [
        "green lentils",
        "coral lentils",
    ],
    "ING006": [
        "basmati rice",
        "short-grain rice",
        "short grain rice",
    ],
    "ING007": [
        "extra virgin olive oil",
        "extra-virgin olive oil",
        "olive oils",
    ],
    "ING008": [
        "garlic cloves",
    ],
}

# New canonical ingredients and their English aliases.
# Arabic and French translations are intentionally left empty
# until verified.
NEW_INGREDIENTS = [
    ("eggplant", ["aubergine", "aubergines", "eggplants"]),
    ("tahini", ["tahini paste"]),
    ("pomegranate seeds", ["pomegranate seed"]),
    ("salt", []),
    ("black pepper", ["black peppercorns", "ground black pepper"]),
    ("white pepper", ["mild white pepper"]),
    ("pine nuts", ["pine nut", "pines nuts"]),
    ("bulgur", ["bulgur wheat", "cracked wheat", "coarse bulgur wheat"]),
    ("flour", ["plain flour", "plain white flour", "all-purpose flour",
               "multi-purpose flour"]),
    ("water", []),
    ("yeast", ["baker yeast", "baker's yeast"]),
    ("sugar", ["caster sugar"]),
    ("lamb", ["minced lamb", "lamb cubed", "ground lamb"]),
    ("beef", ["ground beef", "minced beef"]),
    ("yogurt", ["yoghurt"]),
    ("starch", []),
    ("mint", ["fresh mint"]),
    ("dried mint", ["dry mint"]),
    ("fava beans", ["broad beans"]),
    ("cilantro", ["fresh coriander", "green coriander", "coriander leaves"]),
    ("chili pepper", ["red chili pepper", "red chilli pepper"]),
    ("spinach", ["fresh spinach"]),
    ("basil", ["basil leaves"]),
    ("pita bread", ["pitta bread", "pita"]),
    ("lettuce", ["romaine lettuce"]),
    ("radish", ["radishes"]),
    ("vegetable oil", ["vegetable oils"]),
    ("chicory", ["chicory greens"]),
    ("pomegranate molasses", ["debs roman"]),
    ("potato", ["potatoes"]),
    ("butter", []),
    ("baking soda", ["bicarbonate of soda"]),
    ("sumac", []),
    ("spring onion", ["spring onions", "green onions"]),
    ("vinegar", ["red vinegar"]),
    ("carrot", ["carrots"]),
    ("cardamom", ["green cardamom", "green cardamoms"]),
    ("cinnamon", ["ground cinnamon", "cinnamon powder",
                  "cinnamon stick", "cinnamon sticks"]),
    ("cloves", ["clove"]),
    ("cumin", ["ground cumin"]),
    ("caraway", ["caraway seed", "caraway seeds"]),
    ("allspice", ["all spice"]),
    ("nutmeg", []),
    ("green beans", ["frozen green beans"]),
    ("cabbage", ["cabbage leaves"]),
    ("tomato paste", []),
    ("chicken", ["chicken breast", "breast chicken"]),
    ("sea bass", []),
    ("fish stock", []),
    ("okra", []),
    ("molokhia", ["mouloukhia"]),
    ("white beans", ["white haricot beans", "haricot beans"]),
    ("pearl onion", ["pearl onions", "small pearl onions"]),
    ("red pepper", ["sweet pepper"]),
    ("shallot", ["shallots"]),
    ("red wine vinegar", []),
]


def clean(value):
    return " ".join(value.casefold().strip().split())


with DB_PATH.open("r", encoding="utf-8") as file:
    data = json.load(file)

ingredients = data["ingredients"]

# Index existing aliases.
alias_to_id = {}

for ingredient in ingredients:
    for aliases in ingredient.get("names", {}).values():
        for alias in aliases:
            alias_to_id[clean(alias)] = ingredient["id"]

# Add aliases to existing canonical ingredients.
added_aliases = 0

for ingredient_id, aliases in EXISTING_ALIASES.items():
    ingredient = next(
        (x for x in ingredients if x["id"] == ingredient_id),
        None
    )

    if ingredient is None:
        print(f"[WARNING] Missing existing ID: {ingredient_id}")
        continue

    english_names = ingredient["names"].setdefault("en", [])

    for alias in aliases:
        key = clean(alias)

        if key in alias_to_id:
            if alias_to_id[key] != ingredient_id:
                print(f"[CONFLICT] {alias}: {alias_to_id[key]}")
            continue

        english_names.append(alias)
        alias_to_id[key] = ingredient_id
        added_aliases += 1

# Generate the next available canonical ID.
existing_numbers = [
    int(x["id"][3:])
    for x in ingredients
    if x.get("id", "").startswith("ING")
    and x["id"][3:].isdigit()
]

next_number = max(existing_numbers, default=0) + 1

added_ingredients = 0

for canonical_name, aliases in NEW_INGREDIENTS:
    all_names = [canonical_name] + aliases

    # Skip if a canonical name or alias already exists.
    existing_ids = {
        alias_to_id[clean(name)]
        for name in all_names
        if clean(name) in alias_to_id
    }

    if existing_ids:
        print(
            f"[EXISTS] {canonical_name}: "
            f"{', '.join(sorted(existing_ids))}"
        )
        continue

    ingredient_id = f"ING{next_number:03d}"

    record = {
        "id": ingredient_id,
        "names": {
            "en": all_names,
            "ar": [],
            "fr": []
        }
    }

    ingredients.append(record)

    for name in all_names:
        alias_to_id[clean(name)] = ingredient_id

    print(f"[ADDED] {ingredient_id}: {canonical_name}")

    next_number += 1
    added_ingredients += 1

# Save only after all modifications are prepared.
with DB_PATH.open("w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=4)
    file.write("\n")

print("\nDATABASE EXPANSION COMPLETE")
print("New canonical ingredients:", added_ingredients)
print("New aliases:", added_aliases)
print("Total canonical ingredients:", len(ingredients))
