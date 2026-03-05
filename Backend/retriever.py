# retriever.py
import os
from typing import List, Dict, Tuple

from transcriptionVideo import get_transcript_segments
from textSpitting import chunk_segments
from vectorConversion import embed_texts, embed_query
from vectorDB import (
    build_faiss_index,
    save_faiss_index,
    load_faiss_index,
    save_metadata,
    load_metadata,
)

# Where to store per-video FAISS + metadata
VECTOR_STORE_DIR = os.getenv("VECTOR_STORE_DIR", "vector_store")

def _paths(video_id: str) -> Tuple[str, str]:
    os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
    index_path = os.path.join(VECTOR_STORE_DIR, f"{video_id}.faiss")
    meta_path = os.path.join(VECTOR_STORE_DIR, f"{video_id}.json")
    return index_path, meta_path

def build_or_load_video_index(video_id: str):
    index_path, meta_path = _paths(video_id)

    # Load if exists
    if os.path.exists(index_path) and os.path.exists(meta_path):
        index = load_faiss_index(index_path)
        chunks = load_metadata(meta_path)
        return index, chunks

    # Build: fetch transcript -> chunk -> embed -> index -> persist
    segments = get_transcript_segments(video_id)  # list of {text,start,duration}
    chunks = chunk_segments(segments, chunk_size=1000, chunk_overlap=200)  # [{text,start},...]

    if not chunks:
        raise ValueError("Transcript fetched but produced 0 chunks.")

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts).astype("float32")

    index = build_faiss_index(vectors)

    save_faiss_index(index, index_path)
    save_metadata(chunks, meta_path)

    return index, chunks

def retrieve_top_k_by_video_id(
    video_id: str,
    query: str,
    k: int = 3
) -> Tuple[List[Dict], List[float]]:
    index, chunks = build_or_load_video_index(video_id)

    if not chunks:
        return [], []

    k = max(1, min(k, len(chunks)))

    qvec = embed_query(query).astype("float32").reshape(1, -1)
    distances, ids = index.search(qvec, k)

    top = []
    for i in ids[0].tolist():
        if i < 0 or i >= len(chunks):
            continue
        top.append(chunks[i])

    return top, distances[0].tolist()