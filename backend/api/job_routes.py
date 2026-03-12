from fastapi import APIRouter
import pandas as pd
from backend.database.models import load_jobs_from_db
from backend.services.job_fetcher import fetch_jobs_from_adzuna
from backend.services.matcher import match_jobs

router = APIRouter()

@router.post("/match-jobs")
def recommend_jobs(payload: dict):
    user_skills = payload.get("skills", "")
    fetch = payload.get("fetch", True)
    location = payload.get("location", "india")
    limit = payload.get("limit", 10)

    jobs_df = load_jobs_from_db()

    if fetch:
        query = payload.get("query") or user_skills or "python"
        jobs = fetch_jobs_from_adzuna(query=query, location=location, limit=limit)
        if jobs:
            jobs_df = pd.DataFrame(jobs)

    if jobs_df.empty:
        return []

    return match_jobs(user_skills, jobs_df)

