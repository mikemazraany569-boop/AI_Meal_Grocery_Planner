
import json

import faiss
import numpy as np
import pytest

from src.rag.recipe_index_manager import RecipeIndexManager


@pytest.fixture
def sample_retriever():
    """Create a small retriever-like object with a FAISS index."""

    class MockRetriever:
        def __init__(self):
            self.index = faiss.IndexFlatIP(3)

            embeddings = np.array(
                [
                    [1.0, 0.0, 0.0],
                    [0.0, 1.0, 0.0]
                ],
                dtype="float32"
            )

            self.index.add(embeddings)

            self.documents = [
                {
                    "page_content": "Baba ghanouj with eggplant.",
                    "metadata": {
                        "id": "LB001",
                        "name_en": "Baba ghanouj",
                        "ingredient_ids": ["ING011", "ING012"]
                    }
                },
                {
                    "page_content": "Traditional Lebanese falafel.",
                    "metadata": {
                        "id": "LB005",
                        "name_en": "Falafel",
                        "ingredient_ids": ["ING004"]
                    }
                }
            ]

    return MockRetriever()


@pytest.fixture
def manager(tmp_path):
    """Create an index manager using temporary files."""

    return RecipeIndexManager(
        index_path=tmp_path / "recipes.index",
        documents_path=tmp_path / "recipes.json"
    )


def test_save_index_and_documents(
    sample_retriever,
    manager
):
    """Test saving the FAISS index and recipe documents."""

    result = manager.save(sample_retriever)

    assert manager.index_path.exists()
    assert manager.documents_path.exists()

    assert result["total_documents"] == 2
    assert result["index_size"] == 2


def test_load_index_and_documents(
    sample_retriever,
    manager
):
    """Test loading the saved index and documents."""

    manager.save(sample_retriever)

    class EmptyRetriever:
        def __init__(self):
            self.index = None
            self.documents = []

    new_retriever = EmptyRetriever()

    result = manager.load(new_retriever)

    assert new_retriever.index is not None
    assert len(new_retriever.documents) == 2

    assert result["total_documents"] == 2
    assert result["index_size"] == 2
    assert result["embedding_dimensions"] == 3

    assert (
        new_retriever.documents[0]["metadata"]["id"]
        == "LB001"
    )


def test_save_without_index(manager):
    """Test that saving without a FAISS index raises an error."""

    class EmptyRetriever:
        index = None
        documents = []

    with pytest.raises(
        ValueError,
        match="FAISS index has not been built"
    ):
        manager.save(EmptyRetriever())


def test_load_missing_index_file(manager):
    """Test loading when the FAISS index does not exist."""

    with pytest.raises(
        FileNotFoundError,
        match="FAISS index not found"
    ):
        manager.load(None)


def test_load_missing_documents_file(
    sample_retriever,
    manager
):
    """Test loading when the recipe documents do not exist."""

    faiss.write_index(
        sample_retriever.index,
        str(manager.index_path)
    )

    with pytest.raises(
        FileNotFoundError,
        match="Recipe documents not found"
    ):
        manager.load(None)


def test_load_mismatched_document_count(
    sample_retriever,
    manager
):
    """Test detection of inconsistent index and document counts."""

    faiss.write_index(
        sample_retriever.index,
        str(manager.index_path)
    )

    with manager.documents_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            [sample_retriever.documents[0]],
            file
        )

    class EmptyRetriever:
        index = None
        documents = []

    with pytest.raises(
        ValueError,
        match="Index/document mismatch"
    ):
        manager.load(EmptyRetriever())


def test_load_empty_documents(
    sample_retriever,
    manager
):
    """Test rejection of an empty recipe document list."""

    faiss.write_index(
        sample_retriever.index,
        str(manager.index_path)
    )

    with manager.documents_path.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump([], file)

    class EmptyRetriever:
        index = None
        documents = []

    with pytest.raises(
        ValueError,
        match="Saved recipe documents are empty or invalid"
    ):
        manager.load(EmptyRetriever())
