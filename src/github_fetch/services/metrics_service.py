from github_fetch.schemas.schemas import MetricSchema, RepoSchema, CommitSchema


def _sample_messages(commits: list[CommitSchema], groups: int = 5) -> list[str]:
    if len(commits) <= groups:
        return [c.message for c in commits]
    size = len(commits) / groups
    picked = []
    for i in range(groups):
        chunk = commits[round(i * size):round((i + 1) * size)]
        picked.append(chunk[len(chunk) // 2].message)
    return picked

def calculate_metrics(repo: RepoSchema, commits: list[CommitSchema]) -> MetricSchema:
    user_commits = sorted(
        (c for c in commits if c.author_id == repo.owner_id),
        key=lambda c: c.date,
    )
    if not user_commits:
        return None

    return MetricSchema(
        repo_id=repo.id,
        repo_name=repo.name,
        total_commits=len(commits),
        user_total_commits=len(user_commits),
        user_active_days=len({c.date.date() for c in user_commits}),
        first_commit_date=user_commits[0].date,
        last_commit_date=user_commits[-1].date,
        is_fork=repo.fork,
        commit_messages=_sample_messages(user_commits),
    )
    



   
