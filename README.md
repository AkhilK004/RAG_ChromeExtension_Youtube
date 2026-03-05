# YouTube RAG Assistant

A **Chrome Extension + FastAPI backend** that allows users to **ask questions about any YouTube video**.

The system automatically:

1. Fetches the transcript of the video
2. Chunks the transcript
3. Converts chunks into embeddings
4. Stores them in a vector database
5. Converts the user query into an embedding
6. Retrieves the most relevant transcript chunks
7. Uses an LLM to generate an answer grounded in the video

Users only need to **ask a question** — the system handles the rest.

---

# 🚀 Features

* Ask questions about any YouTube video
* Automatic transcript retrieval
* Retrieval-Augmented Generation (RAG)
* Semantic search with vector embeddings
* Vector database using FAISS
* LLM-powered answers
* Chrome extension interface
* Deployable backend (Render / Docker)

---

# 🧠 System Architecture

```
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
Generate Embeddings
(Sentence Transformers)
      │
      ▼
Store in Vector Database
(FAISS)
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
Return Answer
```

---

# 📂 Project Structure

```
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
```

---

# ⚙️ Backend Components

### api_server.py

FastAPI server exposing API endpoints used by the Chrome extension.

### transcriptionVideo.py

Fetches the transcript of a YouTube video using `youtube-transcript-api`.

### textSpitting.py

Chunks the transcript into manageable segments with timestamps.

### vectorConversion.py

Generates embeddings using:

```
sentence-transformers/all-MiniLM-L6-v2
```

### vectorDB.py

Stores vectors using **FAISS** for fast similarity search.

### retriever.py

Handles:

* transcript chunking
* embedding generation
* vector search

### rag_pipeline.py

Combines retrieved transcript chunks with the user question and sends them to the LLM.

### chatmodel.py

Loads the LLM via HuggingFace Inference API.

---

# 🔧 Local Setup

## 1. Clone repository

```
git clone https://github.com/your-username/youtube-rag-assistant.git
cd youtube-rag-assistant
```

---

## 2. Setup backend

```
cd Backend
python -m venv venv
```

Activate environment

### Windows

```
venv\Scripts\activate
```

### Linux / Mac

```
source venv/bin/activate
```

Install dependencies

```
pip install -r requirements.txt
```

---

## 3. Add HuggingFace token

Create `.env` file inside `Backend` folder

```
HF_TOKEN=your_huggingface_token
```

---

## 4. Run backend

```
uvicorn api_server:app --reload
```

Server will start at

```
http://127.0.0.1:8000
```

Swagger API docs:

```
http://127.0.0.1:8000/docs
```

---

# 🧩 Load Chrome Extension

1. Open Chrome
2. Go to

```
chrome://extensions
```

3. Enable **Developer Mode**
4. Click **Load Unpacked**
5. Select the `ChromeExtension` folder

---

# 🚀 Deploy Backend to Render

1. Push repository to GitHub
2. Create a **Render Web Service**
3. Set:

```
Environment: Docker
Docker Build Context Directory: Backend
```

4. Add environment variable:

```
HF_TOKEN=your_huggingface_token
```

5. Deploy

Backend will be available at:

```
https://your-service.onrender.com
```

---

# 🛠 Technologies Used

* FastAPI
* HuggingFace API
* Sentence Transformers
* FAISS
* Chrome Extension API
* Docker
* Render

---

# 💡 Future Improvements

* persistent vector database
* embedding caching per video
* streaming responses
* multi-video knowledge base
* improved transcript retrieval

---

<img width="1211" height="924" alt="image" src="https://github.com/user-attachments/assets/36f2d17a-0db8-46a9-b23b-caccdfae7d3a" />

