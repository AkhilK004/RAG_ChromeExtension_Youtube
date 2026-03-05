# vectorDB.py
import json
import faiss
from typing import List, Dict

def build_faiss_index(vectors):
    dim = vectors.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(vectors)
    return index

def save_faiss_index(index, path: str) -> None:
    faiss.write_index(index, path)

def load_faiss_index(path: str):
    return faiss.read_index(path)

def save_metadata(chunks: List[Dict], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

def load_metadata(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)