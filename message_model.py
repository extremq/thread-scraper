from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    content: str = ""
    username: str = ""
    timestamp: datetime = datetime.now()
    id: str = 0
    likes: str = 0
