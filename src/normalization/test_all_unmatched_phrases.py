
import json
from pathlib import Path

from src.normalization.ingredient_phrase_normalizer import (
    IngredientPhraseNormalizer,
)


# Original unmatched phrases and their occurrence counts.
unmatched_phrases = [
    ("tomato juice", 5),
    ("pepper", 4),
    ("salt and pepper", 4),
    ("salt to taste", 2),
    ("6 cloves of garlic", 2),
    ("coriander", 2),
    ("Coriander", 1),
    ("Lamb ground onions", 1),
    ("Chichbarak Dough: multi-purpose flour", 1),
    ("water warm to form a paste", 1),
    ("Meat Stuffing: ground beef", 1),
    ("black pepper to taste", 1),
    ("cinnamon powder to taste", 1),
    ("onion finely chopped", 1),
    ("bushel of parsley chopped", 1),
    ("Chich Barak Stew: yogurt", 1),
    ("garlic cloves crushed (optional)", 1),
    ("dried chickpeas (Garbanzo beans)", 1),
    ("Italian parsley (chop away the stems)", 1),
    ("green cilantro (chop away the stems)", 1),
    ("red or yellow onion", 1),
    ("red chili pepper (optional, if spicy falafel is desired)", 1),
    ("Falafel Tahini Sauce Ingredients: Tahini Paste", 1),
    ("garlic cloves, crushed", 1),
    ("tahini and vinegar", 1),
    ("Lettuces or romaine lettuce", 1),
    ("FInely ground beef (or lamb, lean, divided)", 1),
    ("onions (finely chopped)", 1),
    ("small courgettes", 1),
    ("salt and black pepper", 1),
    ("few drops of pomegranate molasses", 1),
    ("white onions, sliced", 1),
    ("Frozen bag green beans", 1),
    ("garlic cloves, peeled", 1),
    ("Cans of chopped tomatoes", 1),
    ("Salt and sweet pepper, to taste", 1),
    ("7 spices", 1),
    ("basic vegetables stuffing", 1),
    ("Green or coral lentils", 1),
    ("Dry dough", 1),
    ("Eggplant, sliced into (you can leave skin on or peel)", 1),
    ("yellow or white onion, diced", 1),
    ("garlic cloves, minced", 1),
    ("low-salt chickpeas", 1),
    ("low-salt diced tomatoes", 1),
    ("Piquant Post Spicy Mint blend", 1),
    ("Pita chips or crusty bread for dipping", 1),
    ("salt and pepper to taste", 1),
    ("Medium fat meat", 1),
    ("Sea bass, scaled and gutted or in fillets", 1),
    ("Meat", 1),
    ("wheat", 1),
    ("Vine leaves", 1),
    ("meat", 1),
    ("Shoulder of lamb", 1),
    ("fresh white haricot beans", 1),
    ("500 ml water or chicken stock", 1),
    ("free-range chicken", 1),
]


def main():
    normalizer = IngredientPhraseNormalizer()

    results = []

    for phrase, occurrences in unmatched_phrases:
        result = normalizer.normalize(phrase)

        results.append({
            "original": phrase,
            "occurrences": occurrences,
            **{
                key: value
                for key, value in result.items()
                if key != "original"
            },
        })

    # Calculate phrase counts and occurrence counts.
    total_occurrences = sum(
        item["occurrences"] for item in results
    )

    statuses = {
        "matched": [],
        "alternatives": [],
        "needs_review": [],
    }

    for item in results:
        statuses[item["status"]].append(item)

    print("=" * 65)
    print("INGREDIENT PHRASE NORMALIZATION REPORT")
    print("=" * 65)

    print("Unique phrases:", len(results))
    print("Total occurrences:", total_occurrences)

    print("\nRESULTS BY STATUS")
    print("-" * 65)

    for status, items in statuses.items():
        occurrences = sum(
            item["occurrences"] for item in items
        )

        print(
            f"{status}: {len(items)} unique phrases, "
            f"{occurrences} occurrences"
        )

    # Detailed report.
    print("\nDETAILED RESULTS")
    print("=" * 65)

    for item in results:
        print(f"\nPhrase: {item['original']}")
        print(f"Occurrences: {item['occurrences']}")
        print(f"Status: {item['status']}")

        for component in item.get("components", []):
            print(
                "  Component:",
                component["canonical_name"],
                "| ID:",
                component["id"],
                "| Status:",
                component["status"],
            )

        for alternative in item.get("alternatives", []):
            print(
                "  Alternative:",
                alternative["canonical_name"],
                "| ID:",
                alternative["id"],
                "| Status:",
                alternative["status"],
            )

        if item.get("review_reason"):
            print("  Review:", item["review_reason"])

    # Save JSON report.
    project_root = Path(__file__).resolve().parents[2]

    output_path = (
        project_root
        / "data"
        / "recipes"
        / "unmatched_ingredient_normalization_report.json"
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "total_unique_phrases": len(results),
        "total_occurrences": total_occurrences,
        "summary": {
            status: {
                "unique_phrases": len(items),
                "occurrences": sum(
                    item["occurrences"] for item in items
                ),
            }
            for status, items in statuses.items()
        },
        "results": results,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print("\n" + "=" * 65)
    print("REPORT SAVED")
    print(output_path)


if __name__ == "__main__":
    main()
