
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent

CSV_PATH = ROOT / "recipes_extended.csv"
OUTPUT_PATH = ROOT / "data" / "recipes" / "lebanese_recipes.json"

SOURCES = {
    "Authentic Lebanese Fattoush": {
        "recipe_id": "LB001",
        "source_name": "No Nonsense Recipes",
        "source_url": "https://nononsense.recipes/authentic-lebanese-fattoush/",
    },
    "Labneh (Lebanese Cream Cheese)": {
        "recipe_id": "LB002",
        "source_name": "Allrecipes",
        "source_url": "https://www.allrecipes.com/recipe/83303/labneh-lebanese-cream-cheese/",
    },
    "Aunt Louise's Baked Kibbeh": {
        "recipe_id": "LB003",
        "source_name": "Allrecipes",
        "source_url": "https://www.allrecipes.com/recipe/267016/aunt-louises-baked-kibbeh/",
    },
}


def parse_list(value):
    if pd.isna(value):
        return []

    if isinstance(value, list):
        return value

    try:
        result = json.loads(value)
        return result if isinstance(result, list) else [result]
    except (json.JSONDecodeError, TypeError):
        return [str(value)]


df = pd.read_csv(CSV_PATH)

recipes = []

for title, source in SOURCES.items():
    matches = df[df["recipe_title"].str.strip() == title]

    if matches.empty:
        print(f"NOT FOUND: {title}")
        continue

    row = matches.iloc[0]

    recipe = {
        **source,
        "name": title,
        "cuisine": "Lebanese",
        "origin_verification_status": "pending",
        "verification_notes": (
            "Candidate identified through recipe title, description, "
            "and external source matching. Further provenance review required."
        ),
        "ingredients": parse_list(row["ingredients"]),
        "instructions": parse_list(row["directions"]),
    }

    recipes.append(recipe)
    print(f"Added: {title}")

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT_PATH.open("w", encoding="utf-8") as file:
    json.dump(
        {"recipes": recipes},
        file,
        ensure_ascii=False,
        indent=4,
    )

print(f"\nCreated: {OUTPUT_PATH}")
print(f"Total recipes: {len(recipes)}")
