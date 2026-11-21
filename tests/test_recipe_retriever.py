
from src.rag.recipe_retriever import RecipeRetriever
import numpy as np

def test_empty_ingredient_ids():
    coverage = RecipeRetriever.calculate_ingredient_coverage(
        [],
        [["ING064", "ING043"]]
    )

    assert coverage == 0.0


def test_exact_ingredient_match():
    coverage = RecipeRetriever.calculate_ingredient_coverage(
        ["ING064"],
        [["ING064"]]
    )

    assert coverage == 1.0


def test_alternative_ingredient_match():
    groups = [["ING064", "ING043"]]

    red_pepper = RecipeRetriever.calculate_ingredient_coverage(
        ["ING064"],
        groups
    )

    sumac = RecipeRetriever.calculate_ingredient_coverage(
        ["ING043"],
        groups
    )

    assert red_pepper == 1.0
    assert sumac == 1.0


def test_partial_ingredient_match():
    groups = [
        ["ING001"],
        ["ING003"],
        ["ING064", "ING043"],
        ["ING008"]
    ]

    coverage = RecipeRetriever.calculate_ingredient_coverage(
        ["ING001", "ING003", "ING043"],
        groups
    )

    assert coverage == 0.75

def test_no_ingredient_groups():
    coverage = RecipeRetriever.calculate_ingredient_coverage(
        ["ING001"],
        []
    )

    assert coverage == 0.0

def test_none_ingredient_ids():
    coverage = RecipeRetriever.calculate_ingredient_coverage(
        None,
        [["ING064", "ING043"]]
    )

    assert coverage == 0.0    


def test_expiry_coverage_with_matching_ingredients():
    groups = [
        ["ING009"],
        ["ING011"],
        ["ING012"],
        ["ING008"]
    ]

    coverage = RecipeRetriever.calculate_expiry_coverage(
        ["ING009", "ING011"],
        groups
    )

    assert coverage == 0.5


def test_expiry_coverage_with_alternative_ingredient():
    groups = [
        ["ING064", "ING043"],
        ["ING001"]
    ]

    coverage = RecipeRetriever.calculate_expiry_coverage(
        ["ING043"],
        groups
    )

    assert coverage == 0.5


def test_expiry_coverage_with_no_expiring_ingredients():
    groups = [
        ["ING009"],
        ["ING011"]
    ]

    coverage = RecipeRetriever.calculate_expiry_coverage(
        [],
        groups
    )

    assert coverage == 0.0


def test_expiry_coverage_with_empty_groups():
    coverage = RecipeRetriever.calculate_expiry_coverage(
        ["ING009"],
        []
    )

    assert coverage == 0.0

class FakeModel:
    """Simulate the sentence-transformer model."""

    def encode(self, texts, **kwargs):
        return np.array([[1.0, 0.0]], dtype="float32")


class FakeIndex:
    """Simulate a FAISS index returning one recipe."""

    def search(self, query_embedding, k):
        scores = np.array([[0.8]], dtype="float32")
        indices = np.array([[0]], dtype="int64")
        return scores, indices


def create_fake_retriever(metadata):
    """Create a retriever without loading the real embedding model."""

    retriever = RecipeRetriever.__new__(RecipeRetriever)

    retriever.model = FakeModel()
    retriever.index = FakeIndex()

    retriever.documents = [
        {
            "page_content": "Lebanese recipe",
            "metadata": metadata
        }
    ]

    return retriever


def test_search_required_ingredient_coverage():
    metadata = {
        "id": "LB001",
        "required_ingredient_groups": [
            ["ING001"],
            ["ING002"]
        ],
        "optional_ingredient_groups": [
            ["ING003"]
        ]
    }

    retriever = create_fake_retriever(metadata)

    results = retriever.search(
        query="Lebanese recipe",
        ingredient_ids=["ING001"]
    )

    result = results[0]

    assert result["ingredient_coverage"] == 0.5
    assert result["matched_required_ingredients"] == 1
    assert result["total_required_ingredients"] == 2


def test_search_missing_required_groups():
    metadata = {
        "id": "LB001",
        "required_ingredient_groups": [
            ["ING001"],
            ["ING002"]
        ],
        "optional_ingredient_groups": []
    }

    retriever = create_fake_retriever(metadata)

    results = retriever.search(
        query="Lebanese recipe",
        ingredient_ids=["ING001"]
    )

    assert results[0]["missing_required_groups"] == [
        ["ING002"]
    ]


def test_optional_ingredients_do_not_affect_combined_score():
    metadata = {
        "id": "LB001",
        "required_ingredient_groups": [
            ["ING001"],
            ["ING002"]
        ],
        "optional_ingredient_groups": [
            ["ING003"]
        ]
    }

    retriever = create_fake_retriever(metadata)

    without_optional = retriever.search(
        query="Lebanese recipe",
        ingredient_ids=["ING001", "ING002"]
    )[0]

    with_optional = retriever.search(
        query="Lebanese recipe",
        ingredient_ids=["ING001", "ING002", "ING003"]
    )[0]

    assert (
        without_optional["score"]
        == with_optional["score"]
    )

    assert (
        without_optional["optional_ingredient_coverage"]
        == 0.0
    )

    assert (
        with_optional["optional_ingredient_coverage"]
        == 1.0
    )



def test_combined_score_calculation():
    metadata = {
        "id": "LB001",
        "required_ingredient_groups": [
            ["ING001"],
            ["ING002"]
        ],
        "optional_ingredient_groups": []
    }

    retriever = create_fake_retriever(metadata)

    results = retriever.search(
        query="Lebanese recipe",
        ingredient_ids=["ING001"],
        expiring_ids=[]
    )

    result = results[0]

    expected_score = (
        0.50 * result["semantic_score"]
        + 0.35 * 0.5
        + 0.15 * 0.0
    )

    assert abs(result["score"] - expected_score) < 0.0001


