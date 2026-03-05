# api_server.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from chatmodel import get_chat_model
from rag_pipeline import answer_query_by_video_id

app = FastAPI(title="YouTube RAG API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

_chat_model = None
def get_model():
    global _chat_model
    if _chat_model is None:
        _chat_model = get_chat_model()
    return _chat_model


class AskRequest(BaseModel):
    video_id: str
    question: str
    k: int = 3


@app.get("/")
def root():
    return {"message": "YouTube RAG API running"}


@app.post("/ask")
def ask(req: AskRequest):
    try:
        answer, sources = answer_query_by_video_id(
            video_id=req.video_id,
            question=req.question,
            chat_model=get_model(),
            k=req.k,
        )
        return {"answer": answer, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))