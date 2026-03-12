from backend.utils.skill_extractor import extract_skills

def match_jobs(user_skills, jobs_df):
    user_skills = [s.strip().lower() for s in user_skills.split(",")]
    results = []

    for _, job in jobs_df.iterrows():
        job_skills = extract_skills(job["description"])
        match_count = len(set(user_skills) & set(job_skills))

        if match_count > 0:
            results.append({
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "matched_skills": match_count
            })

    return sorted(results, key=lambda x: x["matched_skills"], reverse=True)
