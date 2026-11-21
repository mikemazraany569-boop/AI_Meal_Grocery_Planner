
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent

RECIPES_FILE = (
    BASE_DIR / "data" / "recipes" / "lebanese_recipes_enriched.json"
)

INGREDIENTS_FILE = (
    BASE_DIR / "data" / "ingredients" / "ingredients_multilingual.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def ingredient_name(ingredient):
    if not isinstance(ingredient, dict):
        return str(ingredient)

    names = ingredient.get("names", {})
    english = names.get("en", [])

    return english[0] if english else ingredient.get("id", "Unknown")


def classify_record(record):
    alternatives = record.get("alternatives", [])
    components = record.get("components", [])

    if alternatives:
        unresolved = [
            option for option in alternatives
            if not option.get("id")
        ]

        if unresolved:
            return "ALTERNATIVES_WITH_UNRESOLVED_CHOICES"

        return "ALTERNATIVES_WITH_VALID_CHOICES"

    if components:
        unresolved = [
            component for component in components
            if not component.get("ingredient_id")
            and not component.get("id")
        ]

        if unresolved:
            return "COMPOSITE_WITH_UNRESOLVED_COMPONENTS"

        return "COMPOSITE_WITH_VALID_COMPONENTS"

    if not record.get("ingredient_id") and not record.get("id"):
        return "NO_MAPPING"

    return "REVIEW_STATUS_BUT_MAPPING_EXISTS"


def main():
    recipes_data = load_json(RECIPES_FILE)
    ingredients_data = load_json(INGREDIENTS_FILE)

    recipes = recipes_data["recipes"]
    ingredients = ingredients_data["ingredients"]

    ingredient_lookup = {
        item["id"]: ingredient_name(item)
        for item in ingredients
    }

    grouped = {}
    totals = Counter()

    print("=" * 75)
    print("NEEDS_REVIEW DIAGNOSTIC")
    print("=" * 75)

    for recipe in recipes:
        normalized = recipe.get("ingredients_normalized", [])
        detailed = recipe.get("ingredients_detailed", [])

        for index, record in enumerate(normalized):
            if record.get("status") != "needs_review":
                continue

            category = classify_record(record)
            totals[category] += 1

            if category not in grouped:
                grouped[category] = []

            detail = (
                detailed[index]
                if index < len(detailed)
                else {}
            )

            grouped[category].append({
                "recipe_id": recipe.get("id"),
                "recipe_name": recipe.get("name_en"),
                "index": index,
                "original": record.get("original"),
                "detailed_name": detail.get("name"),
                "alternatives": record.get("alternatives", []),
                "components": record.get("components", []),
            })

    for category, records in grouped.items():
        print(f"\n{'=' * 75}")
        print(f"{category} — {len(records)} records")
        print("=" * 75)

        for item in records:
            print(
                f"\n{item['recipe_id']} - {item['recipe_name']}"
            )
            print(f"Index: {item['index']}")
            print(f"Original: {item['original']}")
            print(f"Detailed ingredient: {item['detailed_name']}")

            if item["alternatives"]:
                print("Alternatives:")
                for option in item["alternatives"]:
                    option_id = option.get("id")
                    option_name = option.get("canonical_name")
                    print(
                        f"  - {option.get('original')}: "
                        f"{option_id or 'UNRESOLVED'} "
                        f"({option_name or 'No canonical name'})"
                    )

            if item["components"]:
                print("Components:")
                for component in item["components"]:
                    component_id = (
                        component.get("ingredient_id")
                        or component.get("id")
                    )
                    print(
                        f"  - {component.get('original')}: "
                        f"{component_id or 'UNRESOLVED'}"
                    )

    print("\n" + "=" * 75)
    print("SUMMARY")
    print("=" * 75)

    for category, count in totals.items():
        print(f"{category}: {count}")

    print(f"\nTotal needs_review records: {sum(totals.values())}")
    print("\nNo files were modified.")


if __name__ == "__main__":
    main()
