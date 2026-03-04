import numpy as np
from typing import List, Dict, Tuple

from textSpitting import split_transcript_with_timestamps
from vectorConversion import embed_texts, embed_query
from vectorDB import build_faiss_index

def retrieve_top_k_from_transcript(
    video_id: str,
    transcript: str,
    query: str,
    k: int = 3
) -> Tuple[List[Dict], List[float]]:
    # chunks: list of dicts: {"text": "...", "start": 123}
    chunks = split_transcript_with_timestamps(transcript)

    texts = [c["text"] for c in chunks]
    vectors = embed_texts(texts).astype("float32")

    index = build_faiss_index(vectors)

    qvec = embed_query(query).astype("float32").reshape(1, -1)
    distances, ids = index.search(qvec, k)

    top = []
    for i in ids[0].tolist():
        top.append(chunks[i])

    return top, distances[0].tolist()