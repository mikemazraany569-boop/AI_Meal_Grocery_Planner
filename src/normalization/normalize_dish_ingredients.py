
import json
from pathlib import Path

from src.normalization.ingredient_phrase_normalizer import (
    IngredientPhraseNormalizer,
)


def main():
    project_root = Path(__file__).resolve().parents[2]

    data_path = (
        project_root
        / "data"
        / "recipes"
        / "lebanese_dishes_reference.json"
    )

    backup_path = (
        project_root
        / "data"
        / "recipes"
        / "lebanese_dishes_reference_backup.json"
    )

    if not backup_path.exists():
        raise FileNotFoundError(
            "Backup file is missing. No changes made."
        )

    with data_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    normalizer = IngredientPhraseNormalizer()

    total_ingredients = 0
    status_counts = {
        "matched": 0,
        "needs_review": 0,
        "alternatives": 0,
    }

    for dish in data["dishes"]:
        normalized = []

        for original in dish["ingredients_original"]:
            result = normalizer.normalize(original)

            normalized.append(result)
            total_ingredients += 1

            status = result.get("status", "needs_review")
            status_counts[status] = status_counts.get(status, 0) + 1

        dish["ingredients_normalized"] = normalized

    # Save to a temporary file first.
    temp_path = data_path.with_suffix(".tmp")

    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    # Validate the temporary file before replacing the original.
    with temp_path.open("r", encoding="utf-8") as file:
        validated_data = json.load(file)

    assert len(validated_data["dishes"]) == 30

    for dish in validated_data["dishes"]:
        assert len(dish["ingredients_original"]) == len(
            dish["ingredients_normalized"]
        )

    temp_path.replace(data_path)

    print("DISH INGREDIENT NORMALIZATION COMPLETE")
    print("Total dishes:", len(data["dishes"]))
    print("Total ingredient entries:", total_ingredients)
    print("Matched:", status_counts["matched"])
    print("Needs review:", status_counts["needs_review"])
    print("Alternatives:", status_counts["alternatives"])
    print("Original ingredients preserved: YES")
    print("Backup preserved: YES")


if __name__ == "__main__":
    main()
