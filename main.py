import httpx
from github_fetch.schemas.schemas import RepoSchema, CommitSchema, MetricSchema
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from typing import Annotated
from github_fetch.services.analyzer import analyse_user_repo

@asynccontextmanager
async def get_github_client(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(
        timeout=30.0,
        headers={"Accept": "application/vnd.github+json"},
    )
    yield
    await app.state.http_client.aclose()

app = FastAPI(lifespan=get_github_client)

BASE_URL = "https://api.github.com"

@app.get("/metrics", response_model=list[MetricSchema])
async def fetch_metrics(username: str = Annotated[str, Query(min_length=1)]):
    client = app.state.http_client
    return await analyse_user_repo(client, username)