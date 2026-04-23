"""
backend/main.py
FastAPI application entry point.
"""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.chat import router

# Load .env before anything else
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
print("APP ID:", ADZUNA_APP_ID)
print("APP KEY:", ADZUNA_APP_KEY)

# ── Logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ──────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AI Job Recommendation Chatbot API starting …")
    # Validate critical env vars at startup
    missing = [
               k for k in ("OPENAI_API_KEY", "ADZUNA_APP_ID", "ADZUNA_APP_KEY") 
               if not os.getenv(k)]
    if missing:
        logger.warning("Missing env vars: %s — some features may fail.", missing)
    yield
    logger.info("Shutting down.")


# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Job Recommendation Chatbot",
    description=(
        "Production-ready RAG pipeline: Adzuna jobs → OpenAI embeddings → "
        "FAISS vector search → GPT-4o-mini recommendations."
    ),
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "AI Job Recommendation Chatbot API",
        "docs": "/docs",
        "health": "/api/v1/health",
        "chat": "/api/v1/chat",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000))
    )