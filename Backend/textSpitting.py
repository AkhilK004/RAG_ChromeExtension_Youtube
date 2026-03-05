# textSpitting.py
import re
from typing import List, Dict, Optional

_TS_RE = re.compile(r"^\s*\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(.*)$")

def parse_bracket_timestamp(ts: str) -> float:
    """
    Parses 'MM:SS' or 'HH:MM:SS' into seconds.
    """
    parts = ts.strip().split(":")
    if len(parts) == 2:
        m, s = parts
        return int(m) * 60 + int(s)
    if len(parts) == 3:
        h, m, s = parts
        return int(h) * 3600 + int(m) * 60 + int(s)
    return 0.0

def parse_transcript_text_to_segments(transcript_text: str) -> List[Dict]:
    """
    Converts extension transcript format:
      [03:07] some text
      [03:12] next text
    into segments: [{"text": "...", "start": 187.0}, ...]
    """
    if not transcript_text:
        return []

    segments: List[Dict] = []
    for raw_line in transcript_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        m = _TS_RE.match(line)
        if not m:
            # If a line doesn't match, append it to the last segment if possible
            if segments:
                segments[-1]["text"] = (segments[-1]["text"] + " " + line).strip()
            else:
                segments.append({"text": line, "start": 0.0})
            continue

        ts_str = m.group(1)
        text = (m.group(2) or "").strip()
        if not text:
            continue

        segments.append({"text": text, "start": float(parse_bracket_timestamp(ts_str))})

    return segments

def chunk_segments(segments, chunk_size=1000, chunk_overlap=200):
    """
    Builds text chunks from timestamped transcript segments.
    Returns: list of dicts: [{"text": chunk_text, "start": start_seconds}, ...]
    """
    chunks = []
    current_text = ""
    current_start = None

    def flush():
        nonlocal current_text, current_start
        text = current_text.strip()
        if text:
            chunks.append({"text": text, "start": float(current_start or 0.0)})
        current_text = ""
        current_start = None

    for seg in segments:
        seg_text = (seg.get("text") or "").strip()
        if not seg_text:
            continue

        seg_start = float(seg.get("start") or 0.0)

        if current_start is None:
            current_start = seg_start

        if len(current_text) + len(seg_text) + 1 > chunk_size and current_text:
            flush()

            if chunk_overlap > 0 and chunks:
                overlap_text = chunks[-1]["text"][-chunk_overlap:]
                current_text = overlap_text + "\n"
                current_start = chunks[-1]["start"]

        current_text += seg_text + "\n"

    flush()
    return chunks

def split_transcript_with_timestamps(
    transcript_text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict]:
    """
    High-level helper used by retriever.py:
    transcript_text -> segments -> chunks
    """
    segments = parse_transcript_text_to_segments(transcript_text)
    return chunk_segments(segments, chunk_size=chunk_size, chunk_overlap=chunk_overlap)