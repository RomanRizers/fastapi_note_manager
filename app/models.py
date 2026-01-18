from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from .db import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)