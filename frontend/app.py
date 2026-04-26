
#Gradio chat UI for the AI Job Recommendation Chatbot.

from __future__ import annotations

import os
import json
import requests
from dotenv import load_dotenv

from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# ── Backend URL ────────────────────────────────────────────────────────────────
API_URL = os.getenv("API_URL") or "http://localhost:8000/chat"

# ── Custom CSS ─────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&display=swap');

/* ── Root variables ─────────────────────────────────────────── */
:root {
    --bg:        #0a0a0f;
    --surface:   #111118;
    --border:    #1e1e2e;
    --accent:    #3b82f6;
    --accent2:   #06b6d4;
    --text:      #e2e8f0;
    --muted:     #64748b;
    --success:   #22c55e;
    --card-bg:   #13131e;
    --radius:    12px;
    --font-head: 'Syne', sans-serif;
    --font-mono: 'DM Mono', monospace;
}

/* ── Global reset ───────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

body, .gradio-container {
    background: var(--bg) !important;
    font-family: var(--font-mono) !important;
    color: var(--text) !important;
    min-height: 100vh;
}

.gradio-container { max-width: 1100px !important; margin: 0 auto !important; }

/* ── Header ─────────────────────────────────────────────────── */
.header-block {
    text-align: center;
    padding: 48px 24px 32px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 32px;
}
.header-block h1 {
    font-family: var(--font-head) !important;
    font-size: clamp(2rem, 5vw, 3.2rem) !important;
    font-weight: 800 !important;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #e2e8f0 30%, var(--accent) 70%, var(--accent2));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 12px !important;
}
.header-block p {
    color: var(--muted);
    font-size: 0.95rem;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin: 0 !important;
}

/* ── Chatbot messages ───────────────────────────────────────── */
.chatbot-wrap { border-radius: var(--radius) !important; overflow: hidden; }

.chatbot { background: var(--surface) !important; border: 1px solid var(--border) !important; }
.chatbot .message { font-family: var(--font-mono) !important; font-size: 0.88rem !important; line-height: 1.7 !important; }
.chatbot .message.user { background: #1a1a2e !important; border-left: 3px solid var(--accent) !important; }
.chatbot .message.bot  { background: var(--card-bg) !important; border-left: 3px solid var(--accent2) !important; }

/* ── Input row ──────────────────────────────────────────────── */
.input-row { display: flex; gap: 12px; align-items: flex-end; }

.query-box textarea {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.9rem !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s;
}
.query-box textarea:focus { border-color: var(--accent) !important; outline: none !important; }
.query-box textarea::placeholder { color: var(--muted) !important; }

/* ── Dropdowns ──────────────────────────────────────────────── */
.gr-dropdown select, .gr-dropdown input {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-family: var(--font-mono) !important;
}

/* ── Buttons ────────────────────────────────────────────────── */
.send-btn button, .clear-btn button {
    font-family: var(--font-head) !important;
    font-weight: 700 !important;
    letter-spacing: 0.05em !important;
    border-radius: var(--radius) !important;
    padding: 12px 28px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
    font-size: 0.8rem !important;
}
.send-btn button {
    background: linear-gradient(135deg, var(--accent), var(--accent2)) !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 4px 20px rgba(59,130,246,0.3) !important;
}
.send-btn button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 28px rgba(59,130,246,0.45) !important;
}
.clear-btn button {
    background: transparent !important;
    border: 1px solid var(--border) !important;
    color: var(--muted) !important;
}
.clear-btn button:hover { border-color: var(--muted) !important; color: var(--text) !important; }

/* ── Job cards panel ────────────────────────────────────────── */
.cards-label {
    font-family: var(--font-head) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.12em !important;
    color: var(--accent) !important;
    margin-bottom: 12px !important;
}
.job-cards-html {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 20px !important;
    max-height: 520px !important;
    overflow-y: auto !important;
}

/* ── Stats bar ──────────────────────────────────────────────── */
.stats-html {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 12px 20px !important;
    font-size: 0.8rem !important;
    color: var(--muted) !important;
    margin-top: 12px !important;
}

/* ── Examples section ───────────────────────────────────────── */
.gr-examples { background: transparent !important; border: none !important; }
.gr-examples button {
    background: var(--card-bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--muted) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.8rem !important;
    padding: 8px 14px !important;
    transition: all 0.2s !important;
}
.gr-examples button:hover { border-color: var(--accent) !important; color: var(--text) !important; }

/* ── Scrollbar ──────────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--muted); }

/* ── Misc ───────────────────────────────────────────────────── */
.label-wrap label { color: var(--muted) !important; font-size: 0.78rem !important; text-transform: uppercase !important; letter-spacing: 0.08em !important; }
footer { display: none !important; }
"""


# ── Job card HTML renderer ─────────────────────────────────────────────────────
def _render_job_cards(jobs: list[dict]) -> str:
    if not jobs:
        return (
            '<div style="color:#64748b;text-align:center;padding:40px 0;font-size:0.9rem;">'
            "No job cards to display yet. Send a query above ↑</div>"
        )

    cards_html = []
    for i, job in enumerate(jobs):
        score = job.get("similarity_score")
        score_badge = (
            f'<span style="background:rgba(59,130,246,0.15);color:#3b82f6;'
            f'padding:2px 8px;border-radius:20px;font-size:0.7rem;font-family:\'DM Mono\',monospace;">'
            f"match {score:.0%}</span>"
            if score is not None
            else ""
        )

        salary = ""
        if job.get("salary_min"):
            hi = f" – ₹{job['salary_max']:,.0f}" if job.get("salary_max") else ""
            salary = (
                f'<div style="color:#22c55e;font-size:0.78rem;margin-top:4px;">'
                f"₹{job['salary_min']:,.0f}{hi} / yr</div>"
            )

        apply_btn = ""
        if job.get("apply_link"):
            apply_btn = (
                f'<a href="{job["apply_link"]}" target="_blank" '
                f'style="display:inline-block;margin-top:12px;padding:7px 18px;'
                f'background:linear-gradient(135deg,#3b82f6,#06b6d4);'
                f'color:#fff;border-radius:8px;text-decoration:none;'
                f'font-family:\'Syne\',sans-serif;font-weight:700;font-size:0.75rem;'
                f'letter-spacing:0.06em;text-transform:uppercase;">'
                f"Apply →</a>"
            )

        desc = job.get("description", "")
        if len(desc) > 200:
            desc = desc[:200] + "…"

        card = f"""
        <div style="
            background:#13131e;
            border:1px solid #1e1e2e;
            border-radius:10px;
            padding:16px 18px;
            margin-bottom:12px;
            transition:border-color 0.2s;
        ">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;flex-wrap:wrap;">
                <div>
                    <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1rem;color:#e2e8f0;">
                        {job.get('title','Untitled')}
                    </div>
                    <div style="color:#06b6d4;font-size:0.82rem;margin-top:2px;">
                        {job.get('company','Unknown')}
                    </div>
                    <div style="color:#64748b;font-size:0.78rem;margin-top:2px;">
                        {job.get('location','Not specified')}
                    </div>
                    {salary}
                </div>
                {score_badge}
            </div>
            {f'<div style="color:#94a3b8;font-size:0.8rem;margin-top:10px;line-height:1.6;">{desc}</div>' if desc else ''}
            {apply_btn}
        </div>"""
        cards_html.append(card)

    return "\n".join(cards_html)


def _render_stats(fetched: int, matched: int, query: str) -> str:
    return (
        f'<span style="color:#3b82f6;">⬤</span> '
        f'Fetched <b style="color:#e2e8f0;">{fetched}</b> jobs from Adzuna  ·  '
        f'Top <b style="color:#e2e8f0;">{matched}</b> matched via FAISS  ·  '
        f'Query: <b style="color:#e2e8f0;">{query}</b>'
    )


# ── Core chat function ─────────────────────────────────────────────────────────
def chat_fn(
    message: str,
    history: list,
    location: str,
    num_jobs: int,
) -> tuple:
    """Called by Gradio on every user message."""
    if not message.strip():
        return history, "", "<div style='color:#ef4444'>Please enter a query.</div>", ""

    # Ensure history is list
    history = history or []

    # Add user message (NEW FORMAT)
    history.append({
        "role": "user",
        "content": message
    })

    # Call FastAPI backend
    resp = None
    try:
        resp = requests.post(
            API_URL,
            json={"query": message, "location": location, "limit": num_jobs},
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.ConnectionError:
        err = "Cannot connect to the backend. Make sure FastAPI is running on port 8000."
        history.append({
            "role": "assistant",
            "content": err
        })
        return history, "", err, ""
    except requests.exceptions.HTTPError as e:
        detail = ""
        if resp is not None:
            try:
                detail = resp.json().get("detail", "")
            except Exception:
                pass
        err = f"Backend error {e}. {detail}"
        history.append({
            "role": "assistant",
            "content": err
        })
        return history, "", err, ""
    except Exception as e:
        err = f"Unexpected error: {e}"
        history.append({
            "role": "assistant",
            "content": err
        })
        return history, "", err, ""

    ai_response  = data.get("ai_response", "No response.")
    jobs         = data.get("jobs", [])
    query_used   = data.get("query_used", message)
    jobs_fetched = data.get("jobs_fetched", 0)
    jobs_matched = data.get("jobs_matched", 0)

    # Add assistant response (NEW FORMAT)
    history.append({
        "role": "assistant",
        "content": ai_response
    })

    cards = _render_job_cards(jobs)
    stats = _render_stats(jobs_fetched, jobs_matched, query_used)

    return history, "", cards, stats


# ── Gradio UI ──────────────────────────────────────────────────────────────────
import gradio as gr

HEADER_HTML = """
<div class="header-block">
  <h1>AI Job Recommendation Chatbot</h1>
  <p>Adzuna  ·  OpenAI Embeddings  ·  FAISS  ·  Model: GPT-4o-mini</p>
</div>
"""

EXAMPLE_QUERIES = [
    ["Python developer with Django and REST APIs", "india", 20],
    ["Machine learning engineer NLP experience", "bangalore", 15],
    ["Data analyst fresher SQL Excel Power BI", "remote", 20],
    ["Full stack JavaScript React Node.js", "mumbai", 20],
    ["DevOps engineer AWS Kubernetes CI/CD", "india", 20],
]

with gr.Blocks(title="AI Job Chatbot") as demo:

    gr.HTML(HEADER_HTML)

    with gr.Row():
        # ── Left column: chat ─────────────────────────────────────────────────
        with gr.Column(scale=6):
            chatbot = gr.Chatbot(
                value=[],
                height=440,
                elem_classes=["chatbot-wrap", "chatbot"],
                show_label=False,
            )

            with gr.Row(equal_height=True):
                query_box = gr.Textbox(
                    placeholder="e.g. Python developer with machine learning skills …",
                    show_label=False,
                    lines=2,
                    scale=8,
                    elem_classes=["query-box"],
                )

            with gr.Row():
                with gr.Column(scale=4):
                    location = gr.Dropdown(
                        choices=["india", "bangalore", "mumbai", "delhi", "remote",
                                 "hyderabad", "pune", "chennai", "gb", "us"],
                        value="india",
                        label="Location",
                    )
                with gr.Column(scale=4):
                    num_jobs = gr.Slider(5, 50, value=20, step=5, label="Jobs to fetch")
                with gr.Column(scale=2, elem_classes=["send-btn"]):
                    send_btn = gr.Button("Search →", variant="primary")
                with gr.Column(scale=2, elem_classes=["clear-btn"]):
                    clear_btn = gr.Button("Clear")

            stats_html = gr.HTML(
                '<div class="stats-html">← Send a query to see stats</div>'
            )

            gr.Examples(
                examples=EXAMPLE_QUERIES,
                inputs=[query_box, location, num_jobs],
                label="Try these",
            )

        # ── Right column: job cards ───────────────────────────────────────────
        with gr.Column(scale=5):
            gr.HTML('<div class="cards-label">Top Matched Jobs</div>')
            job_cards = gr.HTML(
                _render_job_cards([]),
                elem_classes=["job-cards-html"],
            )

    # ── Event wiring ──────────────────────────────────────────────────────────
    send_btn.click(
        fn=chat_fn,
        inputs=[query_box, chatbot, location, num_jobs],
        outputs=[chatbot, query_box, job_cards, stats_html],
    )

    query_box.submit(
        fn=chat_fn,
        inputs=[query_box, chatbot, location, num_jobs],
        outputs=[chatbot, query_box, job_cards, stats_html],
    )

    clear_btn.click(
        fn=lambda: ([], "", _render_job_cards([]),
                    '<div class="stats-html">← Send a query to see stats</div>'),
        outputs=[chatbot, query_box, job_cards, stats_html],
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860))
    )