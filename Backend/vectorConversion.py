# vectorConversion.py
from sentence_transformers import SentenceTransformer

_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_texts(texts: list[str]):
    return _model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

def embed_query(query: str):
    return _model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]