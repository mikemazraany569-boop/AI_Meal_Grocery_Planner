
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RECIPES_FILE = (
    BASE_DIR / "data" / "recipes" / "lebanese_recipes_enriched.json"
)


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def main():
    data = load_json(RECIPES_FILE)
    recipes = data["recipes"]

    print("=" * 85)
    print("DETAILED INSPECTION OF UNRESOLVED INGREDIENTS")
    print("=" * 85)

    total = 0

    for recipe in recipes:
        normalized = recipe.get("ingredients_normalized", [])
        detailed = recipe.get("ingredients_detailed", [])

        for index, record in enumerate(normalized):

            if record.get("status") != "needs_review":
                continue

            alternatives = record.get("alternatives", [])
            components = record.get("components", [])

            has_unresolved_alternative = any(
                not option.get("id")
                for option in alternatives
            )

            has_unresolved_component = any(
                not component.get("ingredient_id")
                and not component.get("id")
                for component in components
            )

            no_mapping = (
                not alternatives
                and not components
                and not record.get("ingredient_id")
                and not record.get("id")
            )

            if not (
                no_mapping
                or has_unresolved_alternative
                or has_unresolved_component
            ):
                continue

            total += 1

            detail = (
                detailed[index]
                if index < len(detailed)
                else {}
            )

            print("\n" + "-" * 85)
            print(
                f"{recipe.get('id')} - "
                f"{recipe.get('name_en')}"
            )
            print(f"Ingredient index: {index}")

            print("\nORIGINAL NORMALIZED RECORD:")
            print(json.dumps(
                record,
                ensure_ascii=False,
                indent=2
            ))

            print("\nDETAILED INGREDIENT RECORD:")
            print(json.dumps(
                detail,
                ensure_ascii=False,
                indent=2
            ))

            print("\nRECIPE CONTEXT:")
            print(f"Category: {recipe.get('category')}")
            print(f"Servings: {recipe.get('servings')}")

            print("\nALL RECIPE INGREDIENTS:")
            for ingredient in detailed:
                print(
                    f"- {ingredient.get('name')} | "
                    f"Quantity: {ingredient.get('quantity')} | "
                    f"Unit: {ingredient.get('unit')} | "
                    f"Optional: {ingredient.get('optional')}"
                )

    print("\n" + "=" * 85)
    print(f"TOTAL RECORDS REQUIRING INVESTIGATION: {total}")
    print("No files were modified.")
    print("=" * 85)


if __name__ == "__main__":
    main()
