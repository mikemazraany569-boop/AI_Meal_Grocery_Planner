
import json
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# READ-ONLY CHICKPEA RETRIEVAL SCORE DIAGNOSTIC
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

INDEX_PATH = PROJECT_ROOT / "data" / "vector_store" / "recipes.index"
DOCUMENTS_PATH = PROJECT_ROOT / "data" / "vector_store" / "recipes.json"

MODEL_NAME = "intfloat/multilingual-e5-small"

QUERY = "Recettes libanaises avec des pois chiches"
REQUESTED_INGREDIENT_IDS = {"ING004"}

TARGET_IDS = {"LB003", "LB011", "LB020"}


def calculate_coverage(requested_ids, ingredient_groups):
    if not ingredient_groups:
        return 0.0

    matched_groups = sum(
        1
        for group in ingredient_groups
        if requested_ids.intersection(set(group))
    )

    return matched_groups / len(ingredient_groups)


def main():
    print("=" * 70)
    print("CHICKPEA RETRIEVAL SCORE DIAGNOSTIC — READ ONLY")
    print("=" * 70)

    # Verify existing files.
    for path in (INDEX_PATH, DOCUMENTS_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Required file not found: {path}")

    # Load existing saved index and documents.
    index = faiss.read_index(str(INDEX_PATH))

    with DOCUMENTS_PATH.open("r", encoding="utf-8") as file:
        documents = json.load(file)

    if not isinstance(documents, list):
        raise TypeError("Expected recipes.json to contain a list.")

    if index.ntotal != len(documents):
        raise ValueError(
            f"Index/document mismatch: {index.ntotal} vectors "
            f"but {len(documents)} documents."
        )

    print(f"\nSaved vectors: {index.ntotal}")
    print(f"Saved documents: {len(documents)}")
    print(f"Index dimensions: {index.d}")
    print(f"Query: {QUERY}")
    print(f"Requested ingredient IDs: {sorted(REQUESTED_INGREDIENT_IDS)}")

    # Load the existing local embedding model.
    model = SentenceTransformer(
        MODEL_NAME,
        local_files_only=True
    )

    query_embedding = model.encode(
        ["query: " + QUERY],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    # Search every document to reproduce the retriever's ranking.
    semantic_scores, indices = index.search(
        query_embedding,
        len(documents)
    )

    results = []

    for semantic_score, document_index in zip(
        semantic_scores[0],
        indices[0]
    ):
        if document_index == -1:
            continue

        document = documents[document_index]
        metadata = document["metadata"]

        if "required_ingredient_groups" in metadata:
            required_groups = (
                metadata["required_ingredient_groups"] or []
            )

            coverage = (
                calculate_coverage(
                    REQUESTED_INGREDIENT_IDS,
                    required_groups
                )
                if required_groups
                else 1.0
            )
        else:
            required_groups = metadata.get("ingredient_groups", [])

            coverage = calculate_coverage(
                REQUESTED_INGREDIENT_IDS,
                required_groups
            )

        optional_groups = metadata.get(
            "optional_ingredient_groups",
            []
        )

        optional_coverage = calculate_coverage(
            REQUESTED_INGREDIENT_IDS,
            optional_groups
        )

        matched_required = sum(
            1
            for group in required_groups
            if REQUESTED_INGREDIENT_IDS.intersection(set(group))
        )

        missing_required = [
            group
            for group in required_groups
            if not REQUESTED_INGREDIENT_IDS.intersection(set(group))
        ]

        semantic_score = float(semantic_score)

        # Reproduce the current RecipeRetriever formula.
        combined_score = (
            0.50 * semantic_score
            + 0.35 * coverage
        )

        results.append({
            "id": metadata.get("id"),
            "name": metadata.get("name_en"),
            "semantic_score": semantic_score,
            "ingredient_coverage": coverage,
            "optional_coverage": optional_coverage,
            "matched_required": matched_required,
            "total_required": len(required_groups),
            "missing_required": missing_required,
            "combined_score": combined_score,
        })

    results.sort(
        key=lambda item: item["combined_score"],
        reverse=True
    )

    print("\n" + "=" * 70)
    print("TARGET RECIPE SCORE BREAKDOWN")
    print("=" * 70)

    for rank, result in enumerate(results, start=1):
        if result["id"] not in TARGET_IDS:
            continue

        print(f"\nRank: {rank}")
        print(f"Recipe: {result['id']} — {result['name']}")
        print("-" * 60)

        print(
            f"Semantic score:          "
            f"{result['semantic_score']:.6f}"
        )
        print(
            f"Ingredient coverage:     "
            f"{result['ingredient_coverage']:.6f}"
        )
        print(
            f"Optional coverage:       "
            f"{result['optional_coverage']:.6f}"
        )
        print(
            f"Matched required groups: "
            f"{result['matched_required']}"
        )
        print(
            f"Total required groups:   "
            f"{result['total_required']}"
        )
        print(
            f"Combined score:          "
            f"{result['combined_score']:.6f}"
        )

        print("\nMissing required groups:")
        if result["missing_required"]:
            for group in result["missing_required"]:
                print(f"  {group}")
        else:
            print("  None")

    print("\n" + "=" * 70)
    print("TOP 10 RETRIEVAL RESULTS")
    print("=" * 70)

    for rank, result in enumerate(results[:10], start=1):
        print(
            f"{rank:2}. {result['id']} — {result['name']} "
            f"| final={result['combined_score']:.6f} "
            f"| semantic={result['semantic_score']:.6f} "
            f"| coverage={result['ingredient_coverage']:.6f} "
            f"| matched={result['matched_required']}/"
            f"{result['total_required']}"
        )

    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETED — NO FILES MODIFIED")
    print("=" * 70)


if __name__ == "__main__":
    main()
