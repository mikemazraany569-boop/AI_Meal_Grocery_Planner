
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent

DOCUMENTS_PATH = (
    PROJECT_ROOT
    / "data"
    / "vector_store"
    / "recipes.json"
)

with DOCUMENTS_PATH.open("r", encoding="utf-8") as file:
    documents = json.load(file)

TARGET_IDS = ["LB001", "LB011", "LB020", "LB003"]

print("=" * 70)
print("CHICKPEA RETRIEVAL DIAGNOSTIC — READ ONLY")
print("=" * 70)

for document in documents:

    metadata = document.get("metadata", {})
    recipe_id = metadata.get("id")

    if recipe_id not in TARGET_IDS:
        continue

    groups = metadata.get("required_ingredient_groups", [])
    ingredient_ids = metadata.get("ingredient_ids", [])

    chickpea_groups = [
        group for group in groups
        if "ING004" in group
    ]

    print(f"\n{recipe_id} — {metadata.get('name_en')}")
    print("-" * 60)

    print("Contains chickpeas:", "ING004" in ingredient_ids)
    print("Chickpea groups:", chickpea_groups)
    print("Required groups:", len(groups))
    print("Ingredient IDs:", ingredient_ids)

    content = document.get("page_content", "")

    for line in content.splitlines():
        if any(
            keyword in line.lower()
            for keyword in [
                "chickpea",
                "chickpeas",
                "hummus",
                "hummos",
                "pois chiches",
                "garbanzo"
            ]
        ):
            print("Text:", line)

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETED — NO FILES MODIFIED")
print("=" * 70)
