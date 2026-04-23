"""
models/schema.py
Pydantic models shared across the application.
"""
from pydantic import BaseModel, Field
from typing import Optional


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, description="User's natural-language job query")
    location: str = Field("india", description="Target job location")
    limit: int = Field(20, ge=1, le=50, description="Max jobs to fetch from Adzuna")


class JobCard(BaseModel):
    title: str
    company: Optional[str] = "Unknown"
    location: Optional[str] = "Not specified"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    apply_link: Optional[str] = None
    description: Optional[str] = None
    similarity_score: Optional[float] = None


class ChatResponse(BaseModel):
    ai_response: str
    jobs: list[JobCard]
    query_used: str
    jobs_fetched: int
    jobs_matched: int
