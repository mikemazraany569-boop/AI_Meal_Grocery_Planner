
from functools import lru_cache

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=2)
def load_embedding_model(
    model_name,
    local_files_only=False
):
    """
    Load and cache the multilingual embedding model.

    Cloud deployment:
        local_files_only=False allows downloading from Hugging Face.

    Local offline use:
        local_files_only=True uses an existing local model cache.
    """

    return SentenceTransformer(
        model_name,
        local_files_only=local_files_only
    )


class RecipeRetriever:
    """Retrieve Lebanese recipes using multilingual E5 and FAISS."""

    def __init__(
        self,
        model_name="intfloat/multilingual-e5-small",
        local_files_only=False
    ):

        self.model = load_embedding_model(
            model_name,
            local_files_only
        )

        self.index = None
        self.documents = []

    def build_index(self, documents):
        """Create a FAISS index from recipe documents."""

        if not documents:
            raise ValueError(
                "Cannot build an index from empty documents."
            )

        self.documents = documents

        texts = [
            "passage: " + doc["page_content"]
            for doc in documents
        ]

        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        self.index = faiss.IndexFlatIP(
            embeddings.shape[1]
        )

        self.index.add(embeddings)

        return self.index.ntotal

    @staticmethod
    def calculate_ingredient_coverage(
        requested_ids,
        ingredient_groups
    ):
        """Calculate coverage, treating alternatives as one group."""

        available_ids = set(requested_ids or [])

        if not ingredient_groups:
            return 0.0

        matched_groups = sum(
            1
            for group in ingredient_groups
            if available_ids.intersection(set(group))
        )

        return matched_groups / len(ingredient_groups)

    @staticmethod
    def calculate_expiry_coverage(
        expiring_ids,
        ingredient_groups
    ):
        """Calculate the proportion of required groups containing expiring ingredients."""

        expiring_ids = set(expiring_ids or [])

        if not ingredient_groups:
            return 0.0

        matched_groups = sum(
            1
            for group in ingredient_groups
            if expiring_ids.intersection(set(group))
        )

        return matched_groups / len(ingredient_groups)

    def search(
        self,
        query,
        top_k=5,
        ingredient_ids=None,
        expiring_ids=None
    ):
        """
        Search recipes using semantic relevance,
        ingredient availability and expiry priority.
        """

        if self.index is None:
            raise ValueError(
                "FAISS index has not been built."
            )

        if not isinstance(query, str) or not query.strip():
            raise ValueError(
                "Query must be a non-empty string."
            )

        if (
            not isinstance(top_k, int)
            or isinstance(top_k, bool)
            or top_k < 1
        ):
            raise ValueError(
                "top_k must be a positive integer."
            )

        query_embedding = self.model.encode(
            ["query: " + query.strip()],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        requested_ids = set(ingredient_ids or [])
        expiring_ids = set(expiring_ids or [])

        search_k = (
            len(self.documents)
            if requested_ids or expiring_ids
            else min(top_k, len(self.documents))
        )

        scores, indices = self.index.search(
            query_embedding,
            search_k
        )

        results = []

        for semantic_score, idx in zip(
            scores[0],
            indices[0]
        ):

            if idx == -1:
                continue

            document = self.documents[idx]
            metadata = document["metadata"]

            if "required_ingredient_groups" in metadata:
                required_groups = metadata[
                    "required_ingredient_groups"
                ] or []

                coverage = (
                    self.calculate_ingredient_coverage(
                        requested_ids,
                        required_groups
                    )
                    if required_groups
                    else 1.0
                )

            else:
                required_groups = metadata.get(
                    "ingredient_groups",
                    []
                )

                coverage = self.calculate_ingredient_coverage(
                    requested_ids,
                    required_groups
                )

            optional_groups = metadata.get(
                "optional_ingredient_groups",
                []
            )

            optional_coverage = (
                self.calculate_ingredient_coverage(
                    requested_ids,
                    optional_groups
                )
                if optional_groups
                else 0.0
            )

            expiry_coverage = (
                self.calculate_expiry_coverage(
                    expiring_ids,
                    required_groups
                )
                if expiring_ids
                else 0.0
            )

            matched_required = sum(
                1
                for group in required_groups
                if requested_ids.intersection(set(group))
            )

            missing_required_groups = [
                group
                for group in required_groups
                if not requested_ids.intersection(set(group))
            ]

            semantic_score = float(semantic_score)

            if requested_ids or expiring_ids:
                combined_score = (
                    0.50 * semantic_score
                    + 0.35 * coverage
                    + 0.15 * expiry_coverage
                )
            else:
                combined_score = semantic_score

            results.append({
                "score": combined_score,
                "semantic_score": semantic_score,
                "ingredient_coverage": coverage,
                "optional_ingredient_coverage": optional_coverage,
                "expiry_coverage": expiry_coverage,
                "matched_required_ingredients": matched_required,
                "total_required_ingredients": len(required_groups),
                "missing_required_groups": missing_required_groups,
                "matched_expiring_groups": sum(
                    1
                    for group in required_groups
                    if expiring_ids.intersection(set(group))
                ),
                "document": document["page_content"],
                "metadata": metadata
            })

        results.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        return results[:top_k]
