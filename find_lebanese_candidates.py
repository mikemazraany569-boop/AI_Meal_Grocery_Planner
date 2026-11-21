
import pandas as pd
import re
import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DATASET_PATH = PROJECT_ROOT / "recipes_extended.csv"

OUTPUT_PATH = (
    PROJECT_ROOT
    / "data"
    / "recipes"
    / "lebanese_candidates.csv"
)

df = pd.read_csv(
    DATASET_PATH,
    encoding="utf-8",
    low_memory=False
)


# Known Lebanese dish names and alternative spellings.
# These are search terms, NOT automatic proof of origin.

LEBANESE_DISHES = [
    "mujadara",
    "mujaddara",
    "moujadara",
    "tabbouleh",
    "tabouli",
    "fattoush",
    "kibbeh",
    "kibbe",
    "kebbeh",
    "manakish",
    "manoushe",
    "manousheh",
    "kaak",
    "sfiha",
    "lahm bi ajeen",
    "shish barak",
    "mloukhieh",
    "molokhia",
    "sayadieh",
    "sayadiyeh",
    "kousa mahshi",
    "sheikh el mahshi",
    "waraq enab",
    "warak enab",
    "hummus",
    "baba ghanoush",
    "muhammara",
    "labneh",
    "arak"
]

pattern = re.compile(
    "|".join(
        re.escape(dish)
        for dish in LEBANESE_DISHES
    ),
    flags=re.IGNORECASE
)


# Search recipe titles first.
title_matches = df[
    df["recipe_title"]
    .fillna("")
    .str.contains(pattern, na=False)
].copy()


# Search descriptions and ingredients for additional candidates.
other_matches = df[
    (
        df["description"].fillna("")
        + " "
        + df["ingredient_text"].fillna("")
    ).str.contains(pattern, na=False)
].copy()


# Combine candidates without duplicating rows.
candidates = pd.concat(
    [title_matches, other_matches]
).drop_duplicates(subset=["recipe_title"])


# Check exact Lebanese cuisine labels.
def parse_list(value):
    try:
        result = ast.literal_eval(value)
        return result if isinstance(result, list) else []
    except (ValueError, SyntaxError, TypeError):
        return []


cuisine_labels = df["cuisine_list"].apply(parse_list)

explicit_lebanese = cuisine_labels.apply(
    lambda labels: any(
        str(label).strip().lower() == "lebanese"
        for label in labels
    )
)

print("TOTAL RECIPES:", len(df))
print("EXPLICIT LEBANESE LABELS:", explicit_lebanese.sum())
print("TITLE MATCHES:", len(title_matches))
print("ALL CANDIDATES:", len(candidates))

print("\nLEBANESE RECIPE CANDIDATES:\n")

columns = [
    "recipe_title",
    "category",
    "ingredients",
    "directions",
    "cuisine_list"
]

print(
    candidates[columns]
    .head(100)
    .to_string(index=False)
)

OUTPUT_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

candidates.to_csv(
    OUTPUT_PATH,
    index=False,
    encoding="utf-8-sig"
)

print("\nCandidates saved to:")
print(OUTPUT_PATH)
