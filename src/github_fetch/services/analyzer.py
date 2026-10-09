import asyncio
from github_fetch.schemas.schemas import MetricSchema
from github_fetch.services.github_client import get_repos, get_commits
from github_fetch.services.metrics_service import calculate_metrics


async def analyse_user_repo(client, username, top_n=10, max_concurrency=5):
    repos = await get_repos(client, username)
    repos = [r for r in repos if r.commit_url]

    semaphore = asyncio.Semaphore(max_concurrency)

    async def process_repo_commit(repo):
        async with semaphore:
            commits = await get_commits(client, repo.commit_url)
        return calculate_metrics(repo, commits)

    results = await asyncio.gather(
        *(process_repo_commit(repo) for repo in repos), return_exceptions=True
    )
    metrics = [r for r in results if isinstance(r, MetricSchema)]
    metrics.sort(key=lambda m: m.user_total_commits, reverse=True)
    return metrics[:top_n]


