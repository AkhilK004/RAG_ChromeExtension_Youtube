# main.py
from chatmodel import get_chat_model
from rag_pipeline import answer_query

videoID = input("Video ID: ").strip()
query = input("Ask a question: ").strip()

model = get_chat_model()
print(answer_query(videoID, query, model, k=3))