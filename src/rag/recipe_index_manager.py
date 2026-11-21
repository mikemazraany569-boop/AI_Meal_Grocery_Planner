
import json
from pathlib import Path

import faiss


class RecipeIndexManager:
    """Save and load FAISS recipe indexes and their documents."""

    def __init__(
        self,
        index_path="data/vector_store/recipes.index",
        documents_path="data/vector_store/recipes.json"
    ):
        self.index_path = Path(index_path)
        self.documents_path = Path(documents_path)

    @staticmethod
    def _validate_documents(documents):
        """Validate the structure of recipe documents."""

        if not isinstance(documents, list) or not documents:
            raise ValueError(
                "Saved recipe documents are empty or invalid."
            )

        for position, document in enumerate(documents):

            if not isinstance(document, dict):
                raise ValueError(
                    f"Document {position} must be a dictionary."
                )

            if not isinstance(document.get("page_content"), str):
                raise ValueError(
                    f"Document {position} has invalid page_content."
                )

            metadata = document.get("metadata")

            if not isinstance(metadata, dict):
                raise ValueError(
                    f"Document {position} has invalid metadata."
                )

            if not metadata.get("id"):
                raise ValueError(
                    f"Document {position} is missing its recipe ID."
                )

    def save(self, retriever):
        """Save the retriever's FAISS index and recipe documents."""

        if retriever.index is None:
            raise ValueError(
                "Cannot save: FAISS index has not been built."
            )

        if not retriever.documents:
            raise ValueError(
                "Cannot save: recipe documents are empty."
            )

        self._validate_documents(retriever.documents)

        if retriever.index.ntotal != len(retriever.documents):
            raise ValueError(
                "Cannot save: FAISS index and documents do not match."
            )

        # Create parent directories.
        self.index_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.documents_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # Save FAISS index.
        faiss.write_index(
            retriever.index,
            str(self.index_path)
        )

        # Save recipe documents and metadata.
        with self.documents_path.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                retriever.documents,
                file,
                ensure_ascii=False,
                indent=4
            )

        return {
            "index_path": str(self.index_path),
            "documents_path": str(self.documents_path),
            "total_documents": len(retriever.documents),
            "index_size": retriever.index.ntotal
        }

    def load(self, retriever):
        """Load a saved FAISS index and its recipe documents."""

        if not self.index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {self.index_path}"
            )

        if not self.documents_path.exists():
            raise FileNotFoundError(
                f"Recipe documents not found: {self.documents_path}"
            )

        # Load FAISS index.
        index = faiss.read_index(
            str(self.index_path)
        )

        # Load recipe documents.
        with self.documents_path.open(
            "r",
            encoding="utf-8"
        ) as file:
            documents = json.load(file)

        # Preserve the expected empty-document error.
        if not isinstance(documents, list) or not documents:
            raise ValueError(
                "Saved recipe documents are empty or invalid."
            )

        # Check index/document consistency first.
        if index.ntotal != len(documents):
            raise ValueError(
                "Index/document mismatch: "
                f"{index.ntotal} vectors but "
                f"{len(documents)} documents."
            )

        self._validate_documents(documents)

        # Restore retriever state.
        retriever.index = index
        retriever.documents = documents

        return {
            "total_documents": len(documents),
            "index_size": index.ntotal,
            "embedding_dimensions": index.d
        }
