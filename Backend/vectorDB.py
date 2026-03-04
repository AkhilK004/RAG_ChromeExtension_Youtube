# vectorDB.py
import faiss
import numpy as np

from transcriptionVideo import get_transcript_segments
from textSpitting import chunk_segments
from vectorConversion import embed_texts

_CACHE = {}  # video_id -> (index, chunks_with_time)

def build_index(videoID: str):
    if videoID in _CACHE:
        return _CACHE[videoID]

    segments = get_transcript_segments(videoID)
    chunks = chunk_segments(segments, chunk_size=1000, chunk_overlap=200)
    texts = [c["text"] for c in chunks]

    vectors = np.array(embed_texts(texts)).astype("float32")
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    _CACHE[videoID] = (index, chunks)
    return index, chunks