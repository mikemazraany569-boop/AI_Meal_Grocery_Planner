
import json
from collections import Counter
from pathlib import Path

from src.normalization.ingredient_normalizer import IngredientNormalizer

ROOT = Path(__file__).resolve().parents[2]

path = ROOT / "data" / "recipes" / "lebanese_dishes_reference.json"

with path.open("r", encoding="utf-8") as file:
    data = json.load(file)

normalizer = IngredientNormalizer()
unmatched = Counter()

for dish in data["dishes"]:
    for ingredient in dish["ingredients_original"]:
        if normalizer.normalize(ingredient) is None:
            unmatched[ingredient] += 1

print("Unique unmatched phrases:", len(unmatched))
print("Total unmatched occurrences:", sum(unmatched.values()))
print("\nUNMATCHED INGREDIENT PHRASES:\n")

for ingredient, count in unmatched.most_common():
    print(f"{ingredient} (appears {count} times)")
