# 🤖 AI Job Recommendation Chatbot

> **RAG pipeline**: Adzuna live jobs → OpenAI Embeddings → FAISS vector search → GPT-4o-mini recommendations → Gradio chat UI

---

## 📐 Architecture

```
User Query (Gradio UI)
        │
        ▼
  FastAPI  /api/v1/chat
        │
        ├─► 1. Adzuna API  ──────────────────── fetch N live jobs
        │
        ├─► 2. OpenAI Embeddings ────────────── embed all job texts + query
        │         (text-embedding-3-small)
        │
        ├─► 3. FAISS (cosine similarity) ────── top-K most relevant jobs
        │
        ├─► 4. GPT-4o-mini (RAG prompt) ─────── rank + explain + advise
        │
        └─► ChatResponse (AI text + job cards)
```

---

## 📁 Project Structure

```
ai_job_chatbot/
├── backend/
│   ├── main.py                    ← FastAPI app entry point
│   ├── .env                       ← secrets (never commit!)
│   ├── .env.example               ← template for other devs
│   ├── routes/
│   │   └── chat.py                ← /chat endpoint (full pipeline)
│   ├── services/
│   │   ├── adzuna_service.py      ← refactored from job_api.py
│   │   ├── embedding_service.py   ← OpenAI text-embedding-3-small
│   │   ├── vector_store.py        ← FAISS index build + search
│   │   └── llm_service.py         ← GPT-4o-mini RAG prompt
│   └── models/
│       └── schema.py              ← Pydantic request/response models
├── frontend/
│   └── app.py                     ← Gradio chat UI
└── Requirements.txt
```

---

## ⚙️ Setup & Installation

### 1. Clone / Extract the project

```bash
cd ai_job_chatbot
```

### 2. Create & activate virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Mac / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r Requirements.txt
```

### 4. Configure environment variables

```bash
cp backend/.env.example backend/.env
```

Edit `backend/.env`:

```env
OPENAI_API_KEY=sk-your-real-openai-key
ADZUNA_APP_ID=01f53ba1
ADZUNA_APP_KEY=9d9f6575330bb61844e4c1d016000321
ADZUNA_COUNTRY=in
ADZUNA_RESULTS_PER_PAGE=20
FAISS_TOP_K=5
```

---

## 🚀 Running Locally

You need **two terminals** — one for the backend, one for the frontend.

### Terminal 1 — FastAPI Backend

```bash
# from project root
cd ai_job_chatbot
uvicorn backend.main:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     🚀  AI Job Recommendation Chatbot API starting …
```

### Terminal 2 — Gradio Frontend

```bash
# from project root
cd ai_job_chatbot
python frontend/app.py
```

You should see:
```
Running on local URL: http://0.0.0.0:7860
```

Open **http://localhost:7860** in your browser.

---

## 🧪 Testing the API

### Health check

```bash
curl http://localhost:8000/api/v1/health
```

### Chat endpoint

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python developer machine learning",
    "location": "india",
    "limit": 20
  }'
```

### Interactive Swagger UI

Open **http://localhost:8000/docs** — test all endpoints with a visual form.

---

## ☁️ Deployment

### Option A — Render.com

1. Push your project to GitHub (exclude `.env`!)
2. Create two **Web Services** on Render:

**Backend service:**
- Build command: `pip install -r Requirements.txt`
- Start command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Add env vars in the Render dashboard

**Frontend service:**
- Start command: `python frontend/app.py`
- Set `API_URL` env var to your backend Render URL

### Option B — Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

railway login
railway init
railway up
```

Set env vars in the Railway dashboard under **Variables**.

---

## 🧠 How It Works

### What is RAG here?

**Retrieval-Augmented Generation (RAG)** = fetch relevant documents first, then let the LLM reason over them.

| Step | What happens |
|------|-------------|
| **Retrieve** | User query → Adzuna API fetches 20 live jobs |
| **Augment** | Query + job descriptions → embeddings → FAISS finds the 5 most relevant |
| **Generate** | GPT-4o-mini receives query + those 5 jobs → writes ranked recommendations |

Without RAG, GPT would hallucinate job listings. With RAG, it reasons over **real, live data**.

### How embeddings improve matching

Plain keyword search: `"python"` matches any job mentioning python.

Embeddings: `"I know scikit-learn and pandas"` matches *Data Scientist* and *ML Engineer* roles even if the word "python" never appears — because the **semantic meaning** is similar in vector space.

`text-embedding-3-small` converts any text into a 1536-dimensional vector. We compute cosine similarity between the query vector and every job vector. Higher score = closer meaning.

### How the LLM improves recommendations

The LLM doesn't just return a ranked list — it:
- Explains **why** each job fits the user's background
- Lists the **specific skills** needed
- Gives a **tailored tip** per job
- Provides **general career advice** for the query

This turns a raw job listing into a personalised career counsellor response.

---

## 🔐 Security Notes

- Never commit `.env` to git — add it to `.gitignore`
- Rotate Adzuna and OpenAI keys if they appear in public repos
- For production, restrict CORS in `backend/main.py`

---

## 📦 Key Dependencies

| Package | Purpose |
|---------|---------|
| `fastapi` | Async REST API framework |
| `uvicorn` | ASGI server |
| `openai` | Embeddings + GPT-4o-mini |
| `faiss-cpu` | Vector similarity search |
| `httpx` | Async HTTP client for Adzuna |
| `gradio` | Chat UI |
| `pydantic` | Request/response validation |
| `python-dotenv` | `.env` file loading |
