from pydantic import BaseModel
from datetime import date

class ActivityItem(BaseModel):
    date: date
    commits: int
    authors: list[str]