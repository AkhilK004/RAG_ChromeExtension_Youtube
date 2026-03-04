# chat_model.py
import os
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace

load_dotenv()

def get_chat_model(
    repo_id: str = "Qwen/Qwen3-Coder-Next",
    temperature: float = 1.0,
    max_new_tokens: int = 300,
):
    """
    Returns a LangChain Chat Model (ChatHuggingFace) backed by a HuggingFaceEndpoint.
    Requires HF_TOKEN in your environment (.env).
    """
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        raise ValueError("HF_TOKEN not found. Add it to your .env file as HF_TOKEN=...")

    endpoint = HuggingFaceEndpoint(
        repo_id=repo_id,
        task="text-generation",
        huggingfacehub_api_token=hf_token,
    )

    chat_model = ChatHuggingFace(
        llm=endpoint,
        temperature=temperature,
        max_new_tokens=max_new_tokens,
    )

    return chat_model