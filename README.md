# 🎥 YouTube RAG Assistant

A **Chrome Extension + FastAPI backend** that allows users to **ask questions about any YouTube video** using **Retrieval Augmented Generation (RAG)**.

The system automatically extracts the transcript of a YouTube video, converts it into semantic embeddings, retrieves the most relevant segments, and generates answers using an LLM.

✅ Users only need to ask a question — the system handles everything else.

---

## 🏷️ Badges

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-API-green)
![RAG](https://img.shields.io/badge/RAG-LLM-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Demo

### Chrome Extension Interface
<p align="center">
  <img src="https://github.com/user-attachments/assets/36f2d17a-0db8-46a9-b23b-caccdfae7d3a" width="800" alt="Chrome Extension Interface"/>
</p>

### Example Question & Answer
<p align="center">
  <img src="https://github.com/user-attachments/assets/ed67906a-8fa8-4ff4-aaaf-120f8cea9891" width="800" alt="Example Q&A"/>
</p>

### Transcript Retrieval & Context
<p align="center">
  <img src="https://github.com/user-attachments/assets/1d1ab2de-3f8b-4639-9568-a9270b3b4a28" width="800" alt="Transcript Retrieval & Context"/>
</p>

### Backend Processing
<p align="center">
  <img src="https://github.com/user-attachments/assets/b7b94e4b-c4e7-4770-950c-a6af84dbdca4" width="800" alt="Backend Processing"/>
</p>

---

## ✨ Features

- 🎬 Ask questions about any YouTube video
- 📜 Automatic transcript retrieval
- 🧠 Retrieval Augmented Generation (RAG)
- 🔎 Semantic search using vector embeddings
- 🗄️ Vector database powered by **FAISS**
- 🤖 LLM-based answers via **HuggingFace Inference API**
- 🧩 Chrome Extension UI
- ☁️ Deployable backend using **Docker / Render**

---

## 🧠 System Architecture

```text
User Question
      │
      ▼
Chrome Extension
      │
      ▼
FastAPI Backend
      │
      ▼
Fetch YouTube Transcript
      │
      ▼
Chunk Transcript
      │
      ▼
Generate Embeddings (Sentence Transformers)
      │
      ▼
Store in Vector DB (FAISS)
      │
      ▼
Embed User Query
      │
      ▼
Similarity Search (Top-K)
      │
      ▼
Send Context + Question to LLM
      │
      ▼
Generate Answer
      │
      ▼
Return Response to Extension



YouTubeRAG
│
├── Backend
│   ├── api_server.py
│   ├── chatmodel.py
│   ├── rag_pipeline.py
│   ├── retriever.py
│   ├── transcriptionVideo.py
│   ├── textSpitting.py
│   ├── vectorConversion.py
│   ├── vectorDB.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── ChromeExtension
    ├── manifest.json
    ├── content.js
    ├── popup.js
    └── popup.html



Local Setup
1️⃣ Clone the repository
git clone https://github.com/your-username/youtube-rag-assistant.git
cd youtube-rag-assistant
2️⃣ Setup backend
cd Backend
python -m venv venv

Activate environment:

Windows

venv\Scripts\activate

Linux / Mac

source venv/bin/activate

Install dependencies:

pip install -r requirements.txt
3️⃣ Add HuggingFace API Token

Create a .env file inside the Backend folder:

HF_TOKEN=your_huggingface_token
4️⃣ Run the backend
uvicorn api_server:app --reload

Server:

http://127.0.0.1:8000

Swagger docs:

http://127.0.0.1:8000/docs
