from typing import List
from sqlalchemy import String, DateTime, Text, Integer, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.database import Base



class Article(Base):
    __tablename__ = "article"

    url: Mapped[str] = mapped_column(String(2048), primary_key=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    author: Mapped[str] = mapped_column(String(400), nullable=True)
    published_at: Mapped[datetime] = mapped_column(DateTime)
    scraped_at: Mapped[datetime] = mapped_column(DateTime)
    subtitle: Mapped[str] = mapped_column(String(400), nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=True)
    image_url: Mapped[str] = mapped_column(String(400), nullable=True)
