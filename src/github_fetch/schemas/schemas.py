from datetime import datetime
from pydantic import BaseModel, Field


class RepoSchema(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int
    description: str | None
    commit_url: str | None
    fork: bool


class CommitSchema(BaseModel):
    id: str
    author_id: int | None
    date: datetime
    message: str


class MetricSchema(BaseModel):
    repo_id: int
    repo_name: str
    repo_description: str | None
    total_commits: int
    user_total_commits: int
    user_active_days: int
    first_commit_date: datetime
    last_commit_date: datetime
    is_fork: bool
    commit_messages: list[str]
    llm_summary: str | None = None
    llm_rank: int | None = None


class LLMResponseSchema(BaseModel):
    id: int = Field(description="repository id")
    verdict: str = Field(
        description="A concise 2-3 line summary of the developer's contributions"
    )
    strengths: str = Field(
        description="A concise 2-3 line evidence-based strengths demonstrated by the commit history."
    )
    limitations: str = Field(
        description="A concise 2-3 line limitations or uncertainties in the available evidence."
    )
    rank: int = Field(
            description="A rank of the github repo on scale of 1-10 based on the metrics."
        )



    
