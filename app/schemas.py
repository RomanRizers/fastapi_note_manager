from pydantic import BaseModel
from datetime import datetime

class NoteIn(BaseModel):
    title: str
    content: str | None = None

class NoteOut(NoteIn):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True