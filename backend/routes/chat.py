"""
routes/chat.py
FINAL optimized version (fast + safe + clean + caching + rate limiting)
"""

from __future__ import annotations

import time
import logging

from fastapi import APIRouter, HTTPException

from backend.models.schema import ChatRequest, ChatResponse, JobCard
from backend.services.adzuna_service import fetch_jobs_async
from backend.services.llm_service import get_recommendations

# NEW: Redis cache import
from backend.services.cache_service import get_cache, set_cache

router = APIRouter()
logger = logging.getLogger(__name__)


#  RATE LIMITING
last_request_time = {}
RATE_LIMIT_SECONDS = 2


def is_rate_limited(user_id: str):
    now = time.time()
    if user_id in last_request_time:
        if now - last_request_time[user_id] < RATE_LIMIT_SECONDS:
            return True
    last_request_time[user_id] = now
    return False


# ── API ENDPOINT 
@router.post("/chat", response_model=ChatResponse, summary="AI Job Recommendation")
async def chat(request: ChatRequest) -> ChatResponse:
    start_time = time.time()

    query = request.query.strip()
    location = (request.location or "india").strip()
    limit = min(request.limit or 10, 10) 

    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Rate limiting check
    user_id = "default_user"
    if is_rate_limited(user_id):
        return ChatResponse(
            ai_response="Too many requests. Please wait a moment.",
            jobs=[],
            query_used=query,
            jobs_fetched=0,
            jobs_matched=0,
        )

    #Fetch jobs (with REDIS caching)
    try:
        cache_key = f"jobs:{query}:{location}"

        #jobs = await get_cache(cache_key)
        jobs = None

        if not jobs:
            jobs = await fetch_jobs_async(
                keyword=query,
                location=location,
                limit=limit
            )
            await set_cache(cache_key, jobs)

    except Exception as exc:
        logger.error("Adzuna fetch failed: %s", exc)
        raise HTTPException(
            status_code=502,
            detail=f"Job API error: {exc}.",
        )

    # Shorten descriptions (performance boost)
    for job in jobs:
        if job.get("description"):
            job["description"] = job["description"][:300]

    if not jobs:
        return ChatResponse(
            ai_response="Job service temporarily unavailable. Please try again.",
            jobs=[],
            query_used=query,
            jobs_fetched=0,
            jobs_matched=0,
        )

    # ── 2. LLM Recommendation
    try:
        llm_result = await get_recommendations(query=query, jobs=jobs)

    except Exception as exc:
        logger.error("LLM failed, using fallback: %s", exc)

        llm_result = {
            "summary": "Showing available jobs based on your query.",
            "recommendations": [],
            "general_advice": "Refine your search for better matches.",
        }

    # Built AI Response 
    summary = llm_result.get("summary", "")
    recommendations = llm_result.get("recommendations", [])
    advice = llm_result.get("general_advice", "")

    ai_text_parts = []

    if summary:
        ai_text_parts.append(f"**{summary}**\n")

    for rec in recommendations[:3]:
        ai_text_parts.append(
            f"**#{rec.get('rank', '?')} — {rec.get('title', '')} @ {rec.get('company', '')}**\n"
            f"Why: {rec.get('why_good_fit', '')}\n"
            f"Skills: {', '.join(rec.get('key_skills_needed', []))}\n"
            f"Tip: {rec.get('tip', '')}\n"
        )

    if advice:
        ai_text_parts.append(f"**Career advice:** {advice}")

    ai_response = "\n".join(ai_text_parts).strip()

    job_cards = [
        JobCard(
            title=j.get("title", ""),
            company=j.get("company"),
            location=j.get("location"),
            salary_min=j.get("salary_min"),
            salary_max=j.get("salary_max"),
            apply_link=j.get("apply_link"),
            description=j.get("description", ""),
            similarity_score=None,
        )
        for j in jobs
    ]

    logger.info("⏱ Total API Time: %.2f sec", time.time() - start_time)

    return ChatResponse(
        ai_response=ai_response,
        jobs=job_cards,
        query_used=query,
        jobs_fetched=len(jobs),
        jobs_matched=len(job_cards),
    )


# HEALTH CHECK
@router.get("/health", summary="Health check")
async def health():
    return {"status": "ok", "service": "AI Job Recommendation Chatbot"}
