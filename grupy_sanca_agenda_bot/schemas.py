from datetime import datetime

from pydantic import BaseModel


class Event(BaseModel):
    id: int | None = None
    identifier: str
    title: str
    date_time: datetime
    location: str
    description: str
    link: str
