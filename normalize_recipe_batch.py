
import json
from pathlib import Path

from src.normalization.ingredient_normalizer import IngredientNormalizer


# Locate the recipe batch
project_root = Path(__file__).resolve().parent

recipe_path = (
    project_root
    / "data"
    / "recipes"
    / "lebanese_recipes_enriched_batch1.json"
)

normalizer = IngredientNormalizer()


# Ambiguous ingredients with multiple possible alternatives.
# Seven spices is deliberately left unresolved because it is
# a spice blend, not the same ingredient as allspice.
alternative_groups = {
    "ground red pepper or sumac": [
        {
            "original": "ground red pepper",
            "id": "ING064",
            "canonical_name": "red pepper",
            "status": "matched"
        },
        {
            "original": "sumac",
            "id": "ING043",
            "canonical_name": "sumac",
            "status": "matched"
        }
    ],

    "lettuce or white cabbage leaves": [
        {
            "original": "lettuce",
            "id": "ING035",
            "canonical_name": "lettuce",
            "status": "matched"
        },
        {
            "original": "white cabbage leaves",
            "id": "ING055",
            "canonical_name": "cabbage",
            "status": "matched"
        }
    ],

    "seven spices or allspice": [
        {
            "original": "seven spices",
            "id": "ING074",
            "canonical_name": "seven spices",
            "status": "matched"
        },
        {
            "original": "allspice",
            "id": "ING052",
            "canonical_name": "allspice",
            "status": "matched"
        }
    ]
}


# Load recipes
with recipe_path.open("r", encoding="utf-8") as file:
    data = json.load(file)


matched_count = 0
unmatched_count = 0
alternative_count = 0
unmatched_names = []


for recipe in data["recipes"]:

    normalized_ingredients = []

    for ingredient in recipe.get("ingredients_detailed", []):

        original_name = ingredient["name"]
        lookup_name = original_name.strip().casefold()

        # Handle explicit alternatives
        if lookup_name in alternative_groups:

            alternatives = alternative_groups[lookup_name]

            ingredient["ingredient_id"] = None
            ingredient["canonical_name"] = None

            normalized_ingredients.append({
                "original": original_name,
                "components": [],
                "alternatives": alternatives,
                "status": "needs_review"
            })

            alternative_count += 1

            # Count unresolved alternative components
            for alternative in alternatives:
                if alternative["id"] is None:
                    unmatched_count += 1
                    unmatched_names.append(alternative["original"])
                else:
                    matched_count += 1

            continue

        # Normal ingredient normalization
        result = normalizer.normalize(original_name)

        if result:

            ingredient["ingredient_id"] = result["id"]
            ingredient["canonical_name"] = result["canonical_name"]

            component = {
                "original": original_name,
                "id": result["id"],
                "canonical_name": result["canonical_name"],
                "status": "matched"
            }

            matched_count += 1

        else:

            ingredient["ingredient_id"] = None
            ingredient["canonical_name"] = None

            component = {
                "original": original_name,
                "id": None,
                "canonical_name": None,
                "status": "needs_review"
            }

            unmatched_count += 1
            unmatched_names.append(original_name)

        normalized_ingredients.append({
            "original": original_name,
            "components": [component],
            "alternatives": [],
            "status": component["status"]
        })

    recipe["ingredients_normalized"] = normalized_ingredients


# Save updated recipes
with recipe_path.open("w", encoding="utf-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)


# Display report
print("\nINGREDIENT NORMALIZATION REPORT")
print("=" * 45)

print("Recipes processed:", len(data["recipes"]))
print("Matched ingredients:", matched_count)
print("Unmatched components:", unmatched_count)
print("Alternative groups:", alternative_count)

print("\nUNMATCHED INGREDIENTS:")

for name in sorted(set(unmatched_names)):
    print("-", name)

print("\nALTERNATIVE INGREDIENTS:")

for recipe in data["recipes"]:
    for item in recipe.get("ingredients_normalized", []):
        if item["alternatives"]:
            print(f"\n{recipe['id']} - {item['original']}")

            for alternative in item["alternatives"]:
                print(
                    " ",
                    alternative["original"],
                    "| ID:",
                    alternative["id"],
                    "| Status:",
                    alternative["status"]
                )

print("\nUpdated file:", recipe_path)
