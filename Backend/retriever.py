# retriever.py
import re
import numpy as np
from vectorConversion import embed_query
from vectorDB import build_index

TIME_RANGE_RE = re.compile(
    r"(?:from\s*)?(\d{1,2}:\d{2})(?:\s*(?:to|-)\s*)(\d{1,2}:\d{2})",
    re.IGNORECASE
)

def _mmss_to_seconds(t: str) -> int:
    m, s = t.split(":")
    return int(m) * 60 + int(s)

def extract_time_range(query: str):
    """
    Returns (start_sec, end_sec) if query contains 'MM:SS to MM:SS' or 'from MM:SS to MM:SS'.
    Otherwise returns None.
    """
    m = TIME_RANGE_RE.search(query)
    if not m:
        return None
    a = _mmss_to_seconds(m.group(1))
    b = _mmss_to_seconds(m.group(2))
    if b < a:
        a, b = b, a
    return a, b

def retrieve_by_timerange(chunks, start_sec: int, end_sec: int, limit: int = 6):
    """
    Returns chunks whose start time falls within [start_sec, end_sec].
    We also include small padding for better answers.
    """
    pad = 10  # seconds padding on each side
    s = max(0, start_sec - pad)
    e = end_sec + pad

    selected = [c for c in chunks if s <= float(c.get("start", 0.0)) <= e]

    # If nothing found (chunk start times might be sparse), pick nearest chunks
    if not selected:
        # sort by distance to mid
        mid = (start_sec + end_sec) / 2
        selected = sorted(chunks, key=lambda c: abs(float(c.get("start", 0.0)) - mid))[:limit]
    else:
        # keep them in chronological order and limit
        selected = sorted(selected, key=lambda c: float(c.get("start", 0.0)))[:limit]

    sources = [{"text": c.get("text", ""), "start": float(c.get("start", 0.0) or 0.0)} for c in selected]
    return sources

def retrieve_top_k(videoID: str, query: str, k: int = 3):
    index, chunks = build_index(videoID)

    # 1) If query asks for a time range -> time-based retrieval
    tr = extract_time_range(query)
    if tr is not None:
        start_sec, end_sec = tr
        sources = retrieve_by_timerange(chunks, start_sec, end_sec, limit=max(6, k))
        return sources, []  # distances not meaningful here

    # 2) Otherwise normal semantic retrieval
    qvec = embed_query(query)
    qvec = np.array([qvec]).astype("float32")

    distances, ids = index.search(qvec, k)
    top_ids = ids[0].tolist()

    sources = []
    for i in top_ids:
        ch = chunks[i]
        sources.append({"text": ch.get("text", ""), "start": float(ch.get("start", 0.0) or 0.0)})

    return sources, distances[0].tolist()