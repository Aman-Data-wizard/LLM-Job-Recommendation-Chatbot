SKILLS = [
    "python", "sql", "excel", "tableau", "power bi",
    "machine learning", "ai", "data analysis", "data engineer", 
    "data scientist", "Agentic Ai", "deep learning", "natural language processing",
    "computer vision", "big data", "cloud computing", "aws", "azure", "gcp", "Devops",
    "C++ Developer", "Java Developer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Cybersecurity", "networking", "linux", "docker", "kubernetes", "git", "agile",
]

def extract_skills(text):
    if not text:
        return []
    text = text.lower()
    return [skill for skill in SKILLS if skill in text]
