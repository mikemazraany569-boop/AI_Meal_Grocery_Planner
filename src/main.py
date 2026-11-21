import pandas as pd

df = pd.read_csv(r"D:\pythonproject\AI_Meal_Grocery_Planner\recipes_extended.csv")

print("Dataset shape:", df.shape)
print("\nCuisine examples:")
print(df["cuisine_list"].value_counts().head(30))


import ast

def parse_cuisines(value):
    try:
        result = ast.literal_eval(value)
        return result if isinstance(result, list) else []
    except (ValueError, SyntaxError, TypeError):
        return []

df["parsed_cuisines"] = df["cuisine_list"].apply(parse_cuisines)

lebanese = df[
    df["parsed_cuisines"].apply(
        lambda cuisines: "lebanese" in cuisines
    )
]

middle_eastern = df[
    df["parsed_cuisines"].apply(
        lambda cuisines: "middle eastern region" in cuisines
    )
]

print("\nExplicitly Lebanese recipes:", len(lebanese))
print("Middle Eastern region recipes:", len(middle_eastern))

print("\nLebanese recipe examples:")
print(lebanese["recipe_title"].head(20).to_string(index=False))


print("\nMiddle Eastern recipe examples:")

print(
    middle_eastern[
        ["recipe_title", "cuisine_list", "description"]
    ].head(40).to_string(index=False)
)


lebanese_dishes = [
    "tabbouleh",
    "fattoush",
    "kibbeh",
    "mujadara",
    "manakish",
    "manoushe",
    "shish barak",
    "kousa mahshi",
    "hummus",
    "baba ghanoush",
    "warak enab",
    "sfiha",
    "kafta",
    "makanek",
    "sujuk",
    "freekeh",
]

pattern = "|".join(lebanese_dishes)

matches = df[
    df["recipe_title"].str.contains(
        pattern, case=False, na=False, regex=True
    )
]

print("\nPotential Lebanese dish matches:", len(matches))

print(
    matches[
        ["recipe_title", "cuisine_list", "description"]
    ].head(100).to_string(index=False)
)


from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

path = (
    PROJECT_ROOT
    / "data"
    / "recipes"
    / "lebanese_candidates.csv"
)

df = pd.read_csv(path)

SHORTLIST = [
    "Authentic Lebanese Fattoush",
    "Labneh (Lebanese Cream Cheese)",
    "Aunt Louise's Baked Kibbeh",
    "Mujaddara Arabic Lentil Rice",
    "Tabbouleh",
    "Cucumber Salad with Labneh, Za'atar, and Mint",
    "Baba Ghanoush",
    "Falafel with Canned Chickpeas"
]

selected = df[
    df["recipe_title"].isin(SHORTLIST)
]

for _, recipe in selected.iterrows():

    print("\n" + "=" * 70)
    print("RECIPE:", recipe["recipe_title"])
    print("=" * 70)

    print("\nINGREDIENTS:")
    print(recipe["ingredients"])

    print("\nINSTRUCTIONS:")
    print(recipe["directions"])

    print("\nCUISINE:")
    print(recipe["cuisine_list"])

print("Number of candidates:", len(df))

print("\nCandidate recipe titles:")

for i, title in enumerate(
    df["recipe_title"].dropna().drop_duplicates(),
    start=1
):
    print(f"{i}. {title}")
