from job_api import fetch_jobs

jobs = fetch_jobs("python developer")

for job in jobs[:3]:
    print(job)
