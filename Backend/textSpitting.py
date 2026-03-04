# textSpitting.py

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

        # set start time of chunk at the first segment included
        if current_start is None:
            current_start = seg_start

        # if adding this segment would exceed chunk_size -> flush first
        if len(current_text) + len(seg_text) + 1 > chunk_size and current_text:
            flush()

            # overlap: carry last chunk_overlap chars into the next chunk
            if chunk_overlap > 0 and chunks:
                overlap_text = chunks[-1]["text"][-chunk_overlap:]
                current_text = overlap_text + "\n"
                current_start = chunks[-1]["start"]

        current_text += seg_text + "\n"

    flush()
    return chunks