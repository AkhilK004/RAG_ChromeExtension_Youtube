# transcriptionVideo.py
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptFound

def _normalize_items(items):
    out = []
    for it in items:
        if hasattr(it, "text"):
            out.append({
                "text": it.text,
                "start": float(getattr(it, "start", 0.0) or 0.0),
                "duration": float(getattr(it, "duration", 0.0) or 0.0),
            })
        else:
            out.append({
                "text": (it.get("text") or ""),
                "start": float(it.get("start") or 0.0),
                "duration": float(it.get("duration") or 0.0),
            })
    return out

def get_transcript_segments(video_id: str):
    """
    For your youtube_transcript_api version:
    - YouTubeTranscriptApi() instance exists
    - api.fetch(video_id=..., languages=[...]) exists
    - list_transcripts / get_transcript do NOT exist

    So we try multiple languages in order.
    """
    api = YouTubeTranscriptApi()

    # Try English first, then Hindi (add more if you want)
    language_fallbacks = [
        ["en"],
        ["en-US"],
        ["en-GB"],
        ["hi"],  # Hindi auto-generated
    ]

    last_err = None
    for langs in language_fallbacks:
        try:
            items = api.fetch(video_id=video_id, languages=langs)
            return _normalize_items(items)
        except NoTranscriptFound as e:
            last_err = e
            continue

    # If none worked, raise a helpful error
    raise NoTranscriptFound(video_id, [c for group in language_fallbacks for c in group], last_err)