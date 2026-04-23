"""
services/adzuna_service.py
Production-safe version with proper error handling
"""

from __future__ import annotations

import os
import logging
import httpx
import asyncio
import time
from datetime import datetime, timedelta
from functools import lru_cache

logger = logging.getLogger(__name__)

# ── Config ───────────────────────────────────────────────────────────────────
COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")
RESULTS = int(os.getenv("ADZUNA_RESULTS_PER_PAGE", "20"))
HTTP_TIMEOUT = 5.0
CACHE_TTL_SECONDS = 300

BASE_URL = "https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

# ── In-memory cache ──────────────────────────────────────────────────────────
_cached_jobs: dict[tuple[str, str, str, int], dict] = {}


@lru_cache(maxsize=1)
def _async_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(timeout=HTTP_TIMEOUT)


# ── Credential Loader ─────────────────────────────────────────────────────
def _get_credentials():
    app_id = os.getenv("ADZUNA_APP_ID")
    app_key = os.getenv("ADZUNA_APP_KEY")

    if not app_id or not app_key:
        raise EnvironmentError(
            "ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in your .env file."
        )

    return app_id, app_key


# ── Sync Fetch (with retry + safe fallback) ───────────────────────────────
def fetch_jobs(
    keyword: str,
    location: str = "india",
    limit: int = RESULTS,
    country: str = COUNTRY,
    page: int = 1,
) -> list[dict]:

    app_id, app_key = _get_credentials()
    url = BASE_URL.format(country=country, page=page)

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keyword,
        "where": location,
        "results_per_page": min(limit, 10),
    }

    logger.info("Fetching Adzuna jobs: %s", keyword)

    try:
        response = None
        with httpx.Client(timeout=10.0) as client:
            for attempt in range(3):
                response = client.get(url, params=params)

                if response.status_code == 200:
                    break

                if response.status_code == 503:
                    logger.warning("Adzuna 503 - retrying (%d/3)", attempt + 1)
                    time.sleep(2)
                else:
                    logger.error("Adzuna error %s", response.status_code)
                    return []

            if response is None or response.status_code != 200:
                return []

        data = response.json()
        jobs = [_normalise(job) for job in data.get("results", [])]

        return jobs

    except Exception as e:
        logger.error("Adzuna sync error: %s", str(e))
        return []


# ── Async Fetch (with retry + safe fallback) ──────────────────────────────
async def fetch_jobs_async(
    keyword: str,
    location: str = "india",
    limit: int = RESULTS,
    country: str = COUNTRY,
    page: int = 1,
) -> list[dict]:

    app_id, app_key = _get_credentials()
    url = BASE_URL.format(country=country, page=page)

    results_per_page = min(limit, 5)
    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keyword,
        "where": location,
        "results_per_page": results_per_page,
    }

    cache_key = (
        keyword.lower().strip(),
        location.lower().strip(),
        country.lower().strip(),
        results_per_page,
    )
    cached = _cached_jobs.get(cache_key)
    if cached and cached["expires_at"] > datetime.utcnow():
        logger.info("Adzuna cache hit: %s", keyword)
        return cached["jobs"]

    logger.info("Async Adzuna fetch: %s", keyword)

    try:
        response = None
        client = _async_client()
        for attempt in range(3):  # 🔁 retry
            response = await client.get(url, params=params)

            if response.status_code == 200:
                break

            if response.status_code in {429, 503}:
                logger.warning("Adzuna transient error %s - retrying (%d/3)", response.status_code, attempt + 1)
                await asyncio.sleep(2)
            else:
                logger.error("Adzuna error %s", response.status_code)
                return []

        if response is None or response.status_code != 200:
            return []

        data = response.json()
        jobs = [_normalise(job) for job in data.get("results", [])]
        _cached_jobs[cache_key] = {
            "jobs": jobs,
            "expires_at": datetime.utcnow() + timedelta(seconds=CACHE_TTL_SECONDS),
        }

        return jobs

    except Exception as e:
        logger.error("Adzuna async error: %s", str(e))
        return []


# ── Normalizer
def _normalise(item: dict) -> dict:
    return {
        "title": item.get("title", ""),
        "company": item.get("company", {}).get("display_name", "Unknown"),
        "location": item.get("location", {}).get("display_name", "Not specified"),
        "description": item.get("description", "")[:300],
        "salary_min": item.get("salary_min"),
        "salary_max": item.get("salary_max"),
        "apply_link": item.get("redirect_url"),
    }