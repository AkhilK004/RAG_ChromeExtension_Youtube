# vectorConversion.py
from sentence_transformers import SentenceTransformer
import numpy as np

_model = None

def get_embedder():
    global _model
    if _model is None:
        _model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    return _model

def embed_texts(texts: list[str]) -> np.ndarray:
    model = get_embedder()
    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )
    return vectors

def embed_query(query: str) -> np.ndarray:
    model = get_embedder()
    v = model.encode(query, convert_to_numpy=True, normalize_embeddings=True)
    return v