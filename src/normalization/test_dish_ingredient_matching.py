
import json
from pathlib import Path

from src.normalization.ingredient_normalizer import IngredientNormalizer


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DISHES_PATH = (
    PROJECT_ROOT
    / "data"
    / "recipes"
    / "lebanese_dishes_reference.json"
)

with DISHES_PATH.open("r", encoding="utf-8") as file:
    data = json.load(file)

normalizer = IngredientNormalizer()

matched_count = 0
unmatched_count = 0

for dish in data["dishes"]:
    print(f"\n{'=' * 60}")
    print(f"{dish['id']} - {dish['name_en']}")
    print("=" * 60)

    for ingredient in dish["ingredients_original"]:
        result = normalizer.normalize(ingredient)

        if result:
            matched_count += 1
            print(
                f"[MATCH]   {ingredient} -> "
                f"{result['id']} ({result['canonical_name']})"
            )
        else:
            unmatched_count += 1
            print(f"[REVIEW]  {ingredient}")

print("\n" + "=" * 60)
print("MATCHING SUMMARY")
print("=" * 60)
print("Matched ingredients:", matched_count)
print("Unmatched ingredients:", unmatched_count)
print("Total:", matched_count + unmatched_count)
