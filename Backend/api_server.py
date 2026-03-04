from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

from rag_pipeline import answer_query
from chatmodel import get_chat_model


app = FastAPI(title="YouTube RAG API", version="1.0.0")

# ✅ CORS so Chrome extension / frontend can call your hosted API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later you can restrict to chrome-extension://... or your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Load chat model once at startup
chat_model = get_chat_model()

# ✅ Optional API key (recommended for public hosting)
API_KEY = os.getenv("API_KEY")  # set this in Render/Railway env vars


class AskRequest(BaseModel):
    video_id: str
    question: str
    k: int = 3


@app.get("/")
def root():
    return {"message": "YouTube RAG API running"}


@app.post("/ask")
def ask(req: AskRequest, x_api_key: str | None = Header(default=None)):
    # ✅ If API_KEY is set, require it
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        answer, sources = answer_query(
            req.video_id,
            req.question,
            chat_model,
            k=req.k
        )
        return {"answer": answer, "sources": sources}

    except Exception as e:
        # ✅ prevents 500 stack trace leaking; shows clean error to frontend
        raise HTTPException(status_code=500, detail=str(e))