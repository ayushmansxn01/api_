
from sqlalchemy import Column, Integer, String, Boolean,TIMESTAMP
from .database import Base
from sqlalchemy.sql.expression import text
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Post(Base):
    __tablename__="posts"

    id=Column(Integer, primary_key=True, nullable=False)
    title=Column(String,  nullable=False)
    content=Column(String, nullable=False)
    published=Column(Boolean,server_default='True', nullable=False)
    created_at=Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

