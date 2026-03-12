import requests
import json

APP_ID = "01f53ba1"
APP_KEY = "9d9f6575330bb61844e4c1d016000321"

def fetch_jobs(keyword="data analyst", country="in"):
    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": keyword,
        "results_per_page": 20
    }

    response = requests.get(url, params=params)
    print("Status Code:", response.status_code)
    print("Raw Response:", response.text[:500])  # Print first 500 characters for brevity
    
    data = response.json()
    
    print("Keys in Response:", data.keys())
    jobs = []
    
    for job in data.get("results", []):
        jobs.append({
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name"),
            "location": job.get("location", {}).get("display_name"),
            "description": job.get("description"),
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "apply_link": job.get("redirect_url")
        })
    print("Total Jobs Fetched:", len(jobs))
    return jobs


def save_jobs_to_json(jobs, file_path="data/jobs.json"):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4, ensure_ascii=False)
