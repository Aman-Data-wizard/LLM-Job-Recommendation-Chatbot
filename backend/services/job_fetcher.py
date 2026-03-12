import requests
from backend.database.models import insert_jobs
APP_ID = "01f53ba1"
API_KEY = "9d9f6575330bb61844e4c1d016000321"

def fetch_jobs_from_adzuna(query="python", location="india", limit=10):
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
    params = {
        "app_id": APP_ID,
        "app_key": API_KEY,
        "what": query,
        "where": location,
        "results_per_page": limit,
        "content-type": "application/json"
    }

    response = requests.get(url, params=params)
    #Debugging API response
    print("API Response Status:", response.status_code)
    print("Raw response: ", response.text[:300])  # Print first 300 chars of response for debugging

    if response.status_code != 200:
        print("Adzuna API failed with status code:", response.status_code)
        return []
    data = response.json()
    
    jobs = []
    for item in data.get("results", []):
        jobs.append({
            "title": item.get("title"),
            "company": item.get("company", {}).get("display_name"),
            "location": item.get("location", {}).get("display_name"),
            "description": item.get("description"),
            "source": "Adzuna"
        }) 
        
    print("Fetched jobs:", len(jobs))
    
    if jobs:
        insert_jobs(jobs)
        print("Inserted jobs into DB:")
        
    return jobs
        
    