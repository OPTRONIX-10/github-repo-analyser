
import datetime

from pydantic import BaseModel

class RepoSchema(BaseModel):
    id : int
    name:str
    owner_id:int
    description : str | None
    commit_url:str | None
    fork:bool

class CommitSchema(BaseModel):
    id:str
    author_id:int | None
    date: datetime
    message:str

class MetricSchema(BaseModel):
    repo_id:int
    repo_name:str
    total_commits:int
    user_total_commits:int
    user_active_days:int
    first_commit_date:datetime 
    last_commit_date:datetime
    is_fork:bool
    commit_messages:list[str]

    


    
