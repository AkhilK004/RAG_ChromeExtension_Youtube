import numpy as np
from typing import List, Dict, Tuple

from textSpitting import split_transcript_with_timestamps  # ✅ fix name
from vectorConversion import embed_texts, embed_query
from vectorDB import build_faiss_index

def retrieve_top_k_from_transcript(
    video_id: str,
    transcript: str,
    query: str,
    k: int = 3
) -> Tuple[List[Dict], List[float]]:
    chunks = split_transcript_with_timestamps(transcript)
    if not chunks:
        return [], []

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts).astype("float32")

    index = build_faiss_index(vectors)

    qvec = embed_query(query).astype("float32").reshape(1, -1)

    k = max(1, min(k, len(chunks)))  # ✅ clamp k
    distances, ids = index.search(qvec, k)

    top = []
    for i in ids[0].tolist():
        if i < 0 or i >= len(chunks):  # ✅ skip invalid ids
            continue
        top.append(chunks[i])

    return top, distances[0].tolist()