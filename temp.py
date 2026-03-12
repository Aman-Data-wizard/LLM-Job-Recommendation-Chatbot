from job_api import fetch_jobs, save_jobs_to_json

jobs = fetch_jobs(keyword="python developer")
save_jobs_to_json(jobs)

print("Jobs successfully fetched and saved to data/jobs.json")