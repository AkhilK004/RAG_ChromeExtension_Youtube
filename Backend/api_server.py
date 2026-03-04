from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chatmodel import get_chat_model
from rag_pipeline import answer_query_from_transcript_text

app = FastAPI(title="YouTube RAG API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# lazy load (faster boot)
_chat_model = None
def get_model():
    global _chat_model
    if _chat_model is None:
        _chat_model = get_chat_model()
    return _chat_model


class AskWithTranscriptRequest(BaseModel):
    video_id: str
    transcript: str   # FULL transcript text from extension
    question: str
    k: int = 3


@app.get("/")
def root():
    return {"message": "YouTube RAG API running"}


@app.post("/ask_with_transcript")
def ask_with_transcript(req: AskWithTranscriptRequest):
    try:
        answer, sources = answer_query_from_transcript_text(
            video_id=req.video_id,
            transcript=req.transcript,
            question=req.question,
            chat_model=get_model(),
            k=req.k,
        )
        return {"answer": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))