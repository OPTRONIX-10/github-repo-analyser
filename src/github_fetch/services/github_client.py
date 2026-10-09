import httpx
from github_fetch.schemas.schemas import RepoSchema, CommitSchema
from fastapi import HTTPException, Query

BASE_URL = "https://api.github.com"


async def _get_pages(client, url, params=None, max_pages=10):
    per_page = 100
    items = []
    for page in range(1, max_pages + 1):
        response = await client.get(
            url, params={**(params or {}), "page": page, "per_page": per_page}
        )
        if response.status_code == 409:  # empty repo
            return []
        if response.status_code == 404:
            raise HTTPException(404, "Not found")
        if response.status_code in (403, 429):
            remaining = response.headers.get("X-RateLimit-Remaining")
            reset = response.headers.get("X-RateLimit-Reset")
            if remaining == "0":
                raise HTTPException(
                    status_code=429,
                    detail=f"GitHub rate limit exceeded. Reset timestamp: {reset}",
                )

            raise HTTPException(
                status_code=429,
                detail="GitHub API request forbidden or rate-limited",
            )
        response.raise_for_status()

        data = response.json()
        items.extend(data)
        if len(data) < per_page:
            break
    return items


async def get_repos(client, username: str) -> list[RepoSchema]:
    data = await _get_pages(
        client,
        f"{BASE_URL}/users/{username}/repos",
        max_pages=5,
    )
    return [
        RepoSchema(
            id=r["id"],
            name=r["name"],
            owner_id=r["owner"]["id"],
            description=r.get("description"),
            commit_url=r["commits_url"].replace("{/sha}", ""),
            fork=r["fork"],
        )
        for r in data
    ]


async def get_commits(client, commit_url: str, max_pages=10) -> list[CommitSchema]:
    data = await _get_pages(client, commit_url, max_pages=max_pages)
    return [
        CommitSchema(
            id=c["sha"],
            author_id=c["author"]["id"] if c.get("author") else None,
            date=c["commit"]["author"]["date"],
            message=c["commit"]["message"],
        )
        for c in data
    ]
