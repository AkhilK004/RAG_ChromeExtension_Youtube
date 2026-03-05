from chatmodel import get_chat_model
from rag_pipeline import answer_query_from_transcript_text

video_id = input("Video ID: ").strip()
transcript = input("Paste transcript text: ").strip()
question = input("Ask a question: ").strip()

model = get_chat_model()
answer, sources = answer_query_from_transcript_text(video_id, transcript, question, model, k=3)

print("\nANSWER:\n", answer)
print("\nSOURCES:\n", sources)