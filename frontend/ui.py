import html
import os
from datetime import datetime

import gradio as gr
import httpx

API_URL = os.getenv("API_URL", "https://github-repo-analyser-coab.onrender.com")

CSS = """
:root {
  --pow-primary: #F02D7D;
  --pow-bg: #121212;
  --pow-card: #1A1A1A;
  --pow-border: #2C2C2C;
  --pow-text: #F2F2F2;
  --pow-muted: #9B9B9B;
}
.pow-list { display: flex; flex-direction: column; gap: 16px; }
.pow-card { background: var(--pow-card); border: 1px solid var(--pow-border);
            border-radius: 14px; padding: 18px 20px; color: var(--pow-text); }
.pow-card:hover { border-color: var(--pow-primary); }
.pow-head { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.pow-pos { width: 34px; height: 34px; border-radius: 50%; display: flex; align-items: center;
           justify-content: center; font-weight: 700; background: var(--pow-primary); color: #fff; }
.pow-title { font-size: 1.15rem; font-weight: 700; color: var(--pow-text); }
.pow-chip { font-size: 0.75rem; padding: 2px 10px; border-radius: 99px;
            border: 1px solid var(--pow-border); color: var(--pow-muted); }
.pow-chip-accent { border-color: var(--pow-primary); color: var(--pow-primary); }
.pow-desc { color: var(--pow-muted); margin: 8px 0 14px; }
.pow-stats { display: flex; gap: 28px; flex-wrap: wrap; margin: 14px 0 6px; }
.pow-stat small { display: block; color: var(--pow-muted); }
.pow-stat b { font-size: 1.05rem; color: var(--pow-text); }
.pow-bar { height: 8px; border-radius: 99px; background: var(--pow-bg);
           overflow: hidden; margin: 6px 0 14px; }
.pow-bar > span { display: block; height: 100%; background: var(--pow-primary); }
.pow-block { border-left: 3px solid; padding: 8px 12px; margin: 8px 0; border-radius: 4px;
             color: var(--pow-text); background: var(--pow-bg); }
.pow-good { border-color: var(--pow-primary); background: rgba(240, 45, 125, 0.08); }
.pow-warn { border-color: var(--pow-muted); }
.pow-card p { color: var(--pow-text); margin: 6px 0; }
.pow-card details { margin-top: 12px; }
.pow-card summary { cursor: pointer; color: var(--pow-muted); }
.pow-card summary:hover { color: var(--pow-primary); }
.pow-card li { white-space: pre-wrap; margin: 6px 0; color: var(--pow-text); }
.pow-msg { padding: 24px; text-align: center; color: var(--pow-muted); }
"""

colors = {
    "body_background_fill": "#121212",
    "background_fill_primary": "#121212",
    "background_fill_secondary": "#1A1A1A",
    "block_background_fill": "#1A1A1A",
    "block_border_color": "#2C2C2C",
    "border_color_primary": "#2C2C2C",
    "body_text_color": "#F2F2F2",
    "body_text_color_subdued": "#9B9B9B",
    "block_label_background_fill": "#1A1A1A",
    "block_label_text_color": "#9B9B9B",
    "block_title_text_color": "#F2F2F2",
    "input_background_fill": "#121212",
    "input_border_color": "#2C2C2C",
    "input_border_color_focus": "#F02D7D",
    "button_primary_background_fill": "#F02D7D",
    "button_primary_background_fill_hover": "#D6226C",
    "button_primary_text_color": "#FFFFFF",
    "color_accent": "#F02D7D",
}
theme = gr.themes.Base().set(**colors)


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""))


def parse_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def format_span(first: str, last: str) -> str:
    a, b = parse_date(first), parse_date(last)
    if a.date() == b.date():
        return f"{a:%b %d, %Y} · {a:%H:%M}–{b:%H:%M} UTC"
    return f"{a:%b %d, %Y} → {b:%b %d, %Y}"


def render_summary(text: str) -> str:
    parts = []
    for line in (text or "").split("\n"):
        line = line.strip()
        if not line:
            continue
        label, sep, rest = line.partition(":")
        key = label.strip().lower()
        if sep and key in ("strengths", "limitations"):
            cls = "pow-good" if key == "strengths" else "pow-warn"
            parts.append(f'<div class="pow-block {cls}"><b>{esc(label.strip())}:</b>{esc(rest)}</div>')
        else:
            parts.append(f"<p>{esc(line)}</p>")
    return "".join(parts)


def render_card(position: int, r: dict) -> str:
    total = r["total_commits"]
    mine = r["user_total_commits"]
    share = round(100 * mine / total) if total else 0
    days = r["user_active_days"]

    fork = '<span class="pow-chip">Fork</span>' if r.get("is_fork") else ""
    score = r.get("llm_rank")
    score_chip = (
        f'<span class="pow-chip pow-chip-accent">LLM score: {esc(score)}</span>'
        if score is not None
        else ""
    )
    desc = f'<div class="pow-desc">{esc(r.get("repo_description"))}</div>' if r.get("repo_description") else ""

    messages = "".join(f"<li>{esc(m)}</li>" for m in r.get("commit_messages", []))

    return f"""
    <div class="pow-card">
      <div class="pow-head">
        <div class="pow-pos">{position}</div>
        <div class="pow-title">{esc(r["repo_name"])}</div>
        {fork}{score_chip}
      </div>
      {desc}
      <div class="pow-stats">
        <div class="pow-stat"><small>Candidate's commits</small><b>{mine} of {total} ({share}%)</b></div>
        <div class="pow-stat"><small>Active days</small><b>{days}</b></div>
        <div class="pow-stat"><small>Period</small><b>{esc(format_span(r["first_commit_date"], r["last_commit_date"]))}</b></div>
      </div>
      <div class="pow-bar"><span style="width:{share}%"></span></div>
      {render_summary(r.get("llm_summary", ""))}
      <details>
        <summary>Sample commit messages ({len(r.get("commit_messages", []))})</summary>
        <ol>{messages}</ol>
      </details>
    </div>
    """


def message(text: str) -> str:
    return f'<div class="pow-msg">{esc(text)}</div>'


def analyze(username: str):
    username = (username or "").strip()
    if not username:
        yield message("Enter a GitHub username.")
        return

    yield message(f"Analyzing {username}… this can take a minute.")

    try:
        response = httpx.get(f"{API_URL}/metrics", params={"username": username}, timeout=300)
    except httpx.HTTPError as e:
        yield message(f"Could not reach the API: {e}")
        return

    if response.status_code != 200:
        yield message(f"API error {response.status_code}: {response.text[:300]}")
        return

    repos = response.json()
    if not repos:
        yield message("No repositories with this user's commits were found.")
        return

    cards = "".join(render_card(i, r) for i, r in enumerate(repos, start=1))
    yield f'<div class="pow-list">{cards}</div>'


with gr.Blocks(theme=theme, css=CSS, title="GitHub Proof-of-Work Analyzer") as demo:
    gr.Markdown("# GitHub proof-of-work analyzer\nRanks a developer's repositories by evidence of real, sustained work.")
    with gr.Row():
        username = gr.Textbox(label="GitHub username", placeholder="e.g. OPTRONIX-10", scale=4)
        run = gr.Button("Analyze", variant="primary", scale=1)
    output = gr.HTML()
    run.click(analyze, username, output)
    username.submit(analyze, username, output)

if __name__ == "__main__":
    demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860)),
    theme=theme,
    css=CSS,
)