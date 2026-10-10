import httpx
from github_fetch.schemas.schemas import MetricSchema
from contextlib import asynccontextmanager
from fastapi import FastAPI, Query
from typing import Annotated
from github_fetch.services.analyzer import analyse_user_repo
from github_fetch.services.llm_service import add_metrics_and_sort
import os
from dotenv import load_dotenv

load_dotenv(override=True)


@asynccontextmanager
async def get_github_client(app: FastAPI):
    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"
    app.state.http_client = httpx.AsyncClient(
        timeout=30.0,
        headers=headers,
    )
    yield
    await app.state.http_client.aclose()


app = FastAPI(lifespan=get_github_client)

BASE_URL = "https://api.github.com"


@app.get("/metrics", response_model=list[MetricSchema])
async def fetch_metrics(username: str = Annotated[str, Query(min_length=1)]):
    client = app.state.http_client
    metrics = await analyse_user_repo(client, username)
    return await add_metrics_and_sort(metrics)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

