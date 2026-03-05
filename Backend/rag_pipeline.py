#rag_pipeline.py

from typing import List, Dict, Tuple
from retriever import retrieve_top_k_from_transcript

def build_prompt(query: str, contexts: list[str]) -> str:
    context_block = "\n\n---\n\n".join(contexts)
    return f"""You are a helpful assistant.
Answer using ONLY the context. If the answer isn't in the context, say "I don't know."

Context:
{context_block}

User question:
{query}
"""

def answer_query_from_transcript_text(
    video_id: str,
    transcript: str,
    question: str,
    chat_model,
    k: int = 3,
) -> Tuple[str, List[Dict]]:
    sources, _scores = retrieve_top_k_from_transcript(video_id, transcript, question, k=k)

    contexts = [s["text"] for s in sources]
    prompt = build_prompt(question, contexts)

    result = chat_model.invoke(prompt)
    answer = getattr(result, "content", str(result))

    return answer, sources