from src.normalization.ingredient_normalizer import IngredientNormalizer


def test_english_normalization():
    normalizer = IngredientNormalizer()
    result = normalizer.normalize("tomato")

    assert result is not None
    assert result["id"]


def test_french_normalization():
    normalizer = IngredientNormalizer()
    result = normalizer.normalize("tomate")

    assert result is not None


def test_arabic_normalization():
    normalizer = IngredientNormalizer()
    result = normalizer.normalize("طماطم")

    assert result is not None


def test_unknown_ingredient():
    normalizer = IngredientNormalizer()

    assert normalizer.normalize("unknown food xyz") is None


def test_empty_input():
    normalizer = IngredientNormalizer()

    assert normalizer.normalize("") is None