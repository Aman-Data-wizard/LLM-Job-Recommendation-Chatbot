"""
services/llm_service.py
LLM layer WITHOUT embeddings (no RAG, direct job reasoning).
"""

from __future__ import annotations

import os
import json
import logging
from functools import lru_cache

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

CHAT_MODEL = "gpt-4o-mini"


# ── Client ───────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _client() -> AsyncOpenAI:
    key = os.getenv("OPENAI_API_KEY")

    return AsyncOpenAI(
        api_key=key,
        max_retries=0   
    )


# ── Prompts ──────────────────────────────────────────────────────────────
def _build_system_prompt() -> str:
    return (
        "You are an expert career counselor. "
        "You analyse job listings and recommend the best matches.\n\n"
        "Return ONLY valid JSON in this format:\n\n"
        "{\n"
        '  "summary": "<short overview>",\n'
        '  "recommendations": [\n'
        "    {\n"
        '      "rank": 1,\n'
        '      "title": "<job title>",\n'
        '      "company": "<company name>",\n'
        '      "why_good_fit": "<reason>",\n'
        '      "key_skills_needed": ["skill1", "skill2"],\n'
        '      "tip": "<improvement tip>"\n'
        "    }\n"
        "  ],\n"
        '  "general_advice": "<career advice>"\n'
        "}\n"
    )


def _build_user_prompt(query: str, jobs: list[dict]) -> str:
    job_blocks = []

    for i, job in enumerate(jobs, 1):
        block = (
            f"{i}. {job.get('title')} at {job.get('company')} "
            f"({job.get('location')})\n"
            f"{job.get('description', '')[:300]}\n"
        )
        job_blocks.append(block)

    jobs_text = "\n\n".join(job_blocks)

    return (
        f"User query: {query}\n\n"
        f"Here are some job listings:\n\n{jobs_text}\n\n"
        "Recommend the best jobs and explain why they match."
    )


# ── LLM Main Function API Response
async def get_recommendations(
    query: str,
    jobs: list[dict],
    temperature: float = 0.4,
) -> dict:

    if not jobs:
        return {
            "summary": "No matching jobs found.",
            "recommendations": [],
            "general_advice": "Try different keywords.",
        }

    system_prompt = _build_system_prompt()
    user_prompt = _build_user_prompt(query, jobs)

    try:
        client = _client()

        # NO RETRIES and  HARD TIMEOUT
        response = await client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=400,
            timeout=5  
        )

        raw = response.choices[0].message.content

        if not raw:
            raise ValueError("Empty LLM response")

        return json.loads(raw)

    except Exception as e:
        logger.warning("LLM failed → using fallback: %s", e)

        # INSTANT FALLBACK (NO WAIT)
        return {
            "summary": "Showing best available job matches based on your query.",
            "recommendations": [],
            "general_advice": "Upgrade AI quota for smarter recommendations.",
        }