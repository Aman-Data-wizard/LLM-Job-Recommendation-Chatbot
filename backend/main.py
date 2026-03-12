from fastapi import FastAPI
from backend.api.job_routes import router
from backend.database.models import create_jobs_table
from backend.services.job_fetcher import fetch_jobs_from_adzuna  
app = FastAPI(title="Job Recommendation API")

create_jobs_table()
app.include_router(router)

@app.get("/")
def root():
    return {"status": "API running"}
@app.post("/fetch-jobs")
def fetch_jobs_endpoint():
    jobs = fetch_jobs_from_adzuna()
    return {"message": f"{len(jobs)} jobs fetched and stored"}
