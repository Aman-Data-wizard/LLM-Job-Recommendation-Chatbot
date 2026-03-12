import gradio as gr
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/match-jobs"

def recommend_jobs(user_input):
    response = requests.post(API_URL, json={
        "skills": user_input,
        "fetch": True,
        "limit": 20
    })

    if response.status_code != 200:
        return pd.DataFrame(columns=["Job Title", "Company", "Location", "Matched Skills"])


    jobs = response.json()
    print("FRONTEND DEBUG", jobs)
    if not jobs:
        return pd.DataFrame(columns=["Job Title", "Company", "Location", "Matched Skills"])

    return pd.DataFrame(jobs)

demo = gr.Interface(
    fn=recommend_jobs,
    inputs=gr.Textbox(label="Enter your skills (comma separated)"),
    outputs=gr.Dataframe(),
    title="Job Recommendation Chatbot",
    description="Get job recommendations based on your skills"
)

demo.launch()
