# GitHub Proof-of-Work Analyzer

FastAPI and Gradio application that fetches a GitHub user's repositories and
commit history, calculates contribution metrics, and uses Gemini to generate an
evidence-based evaluation.

## Requirements

- Python 3.12 or newer
- [`uv`](https://docs.astral.sh/uv/)
- A GitHub personal access token
- A Gemini API key

## Setup

From the project root:

```powershell
cd "D:\ABHISHEK\llm-engineering\github_fetch"
uv sync
```

Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_token
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit `.env` or expose either key in source control.

## Run the application

Run the FastAPI backend first:

```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend is available at:

- API: <http://127.0.0.1:8000>
- Swagger documentation: <http://127.0.0.1:8000/docs>

In a second terminal, start the Gradio UI:

```powershell
cd "D:\ABHISHEK\llm-engineering\github_fetch"
& ".\.venv\Scripts\python.exe" ui.py
```

Open the local URL printed by Gradio, normally
<http://127.0.0.1:7860>.

The UI expects the backend at `http://localhost:8000`. To use another backend
URL, set `API_URL` before starting the UI:

```powershell
$env:API_URL = "http://127.0.0.1:8001"
& ".\.venv\Scripts\python.exe" ui.py
```

## API

The current endpoint is:

```text
GET /metrics?username=<github-username>
```

Example:

```text
http://127.0.0.1:8000/metrics?username=octocat
```

The endpoint fetches repositories and commits from GitHub, calculates metrics,
and sends the first resulting repository metric to Gemini for structured
evaluation.

## Project structure

```text
.
├── main.py
├── ui.py
├── pyproject.toml
├── uv.lock
└── src/
    └── github_fetch/
        ├── schemas/
        │   └── schemas.py
        └── services/
            ├── analyzer.py
            ├── github_client.py
            ├── llm_service.py
            └── metrics_service.py
```

- `main.py`: FastAPI application and `/metrics` endpoint.
- `ui.py`: Gradio frontend.
- `github_client.py`: GitHub API pagination and response parsing.
- `analyzer.py`: Repository and commit analysis orchestration.
- `metrics_service.py`: Contribution metric calculation.
- `llm_service.py`: Gemini structured evaluation.
- `schemas.py`: Pydantic request/response models.

## GitHub rate limits

One `/metrics` request can make many GitHub API requests because repository and
commit data are paginated. Use an authenticated `GITHUB_TOKEN`, avoid repeated
refreshes while testing, and keep the configured page and concurrency limits
reasonable. GitHub responses with status `403` or `429` indicate that the
request was forbidden or rate-limited.

## Troubleshooting

### `uv trampoline failed to canonicalize script path`

On Windows, run Uvicorn through the project interpreter instead of the
`fastapi` launcher:

```powershell
& ".\.venv\Scripts\python.exe" -m uvicorn main:app --reload
```

### `cannot import name '__version__' from 'websockets'`

Repair the dependency in the project environment:

```powershell
uv pip install --python ".\.venv\Scripts\python.exe" --reinstall websockets
```

### Gemini authentication errors

Confirm that `.env` exists in the project root and contains a valid
`GEMINI_API_KEY`. Restart the backend after changing environment variables.

### The UI says it cannot reach the API

Confirm that the backend is running on port `8000` before starting or using the
Gradio UI.