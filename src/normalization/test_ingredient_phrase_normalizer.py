from src.normalization.ingredient_phrase_normalizer import (
    IngredientPhraseNormalizer,
)


normalizer = IngredientPhraseNormalizer()

test_phrases = [
    "salt to taste",
    "6 cloves of garlic",
    "salt and pepper",
    "salt and black pepper",
    "salt and pepper to taste",
    "Chichbarak Dough: multi-purpose flour",
    "Meat Stuffing: ground beef",
    "dried chickpeas (Garbanzo beans)",
    "500 ml water or chicken stock",
    "pepper",
    "coriander",
    "tomato juice",
]

for phrase in test_phrases:
    result = normalizer.normalize(phrase)

    print("\nOriginal:", phrase)
    print("Status:", result["status"])
    print("Components:", result["components"])
    print("Alternatives:", result["alternatives"])

    if "review_reason" in result:
        print("Review reason:", result["review_reason"])