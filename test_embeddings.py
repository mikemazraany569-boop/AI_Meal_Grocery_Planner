from sentence_transformers import SentenceTransformer

print("Loading Multilingual E5...")

model = SentenceTransformer(
    "intfloat/multilingual-e5-small"
)

sentences = [
    "passage: Lebanese chicken and rice",
    "passage: دجاج مع الأرز",
    "passage: Poulet avec du riz"
]

embeddings = model.encode(
    sentences,
    normalize_embeddings=True
)

print("Embedding shape:", embeddings.shape)
print("Model loaded successfully!")