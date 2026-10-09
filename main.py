import httpx
from github_fetch.schemas.schemas import RepoSchema, CommitSchema, MetricSchema
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from typing import Annotated

@asynccontextmanager
async def get_github_client(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=30.0,
        headers={"Accept": "application/vnd.github+json"},
    )
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=get_github_client)

base_url = "https://api.github.com"

@app.get("/commits", response_model = list[CommitSchema])
async def fetch_commits(commit_url: str = Annotated[str, Query(min_length=1)]):
    client = app.state.http_client
    commits = []
    page = 1
    per_page = 100

    while True:
        params = {"page": page, "per_page": per_page}
        response = await client.get(commit_url, params=params)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        if not data:
            break

        for commit in data:
            commits.append(CommitSchema(
                id=commit["sha"],
                author_id=commit["author"]["id"] if commit.get("author") else None,
                date=commit["commit"]["author"]["date"],
                message=commit["commit"]["message"]
            ))

        page += 1
    return commits




