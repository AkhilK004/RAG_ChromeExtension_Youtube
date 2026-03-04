# rag_pipeline.py
from retriever import retrieve_top_k

def format_time(seconds: float) -> str:
    seconds = int(max(0, seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"

def build_prompt(query: str, sources: list[dict]) -> str:
    context_lines = []
    for idx, src in enumerate(sources, 1):
        ts = format_time(src["start"])
        context_lines.append(f"[{idx}] ({ts}) {src['text']}")

    context_block = "\n\n---\n\n".join(context_lines)

    return f"""You are a helpful assistant.
Answer using ONLY the context sources. If the answer isn't in the sources, say "I don't know."
When possible, cite sources like [1], [2].

Sources:
{context_block}

User question:
{query}
"""

def answer_query(videoID, query, chat_model, k=3):
    sources, _scores = retrieve_top_k(videoID, query, k=k)
    prompt = build_prompt(query, sources)
    result = chat_model.invoke(prompt)
    answer = getattr(result, "content", str(result))

    # return both answer and sources (for UI)
    return answer, sources