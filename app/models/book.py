from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(150), nullable=False)
    isbn = Column(String(13), unique=True, nullable=False, index=True)
    genre = Column(String(50), nullable=True)
    published_year = Column(Integer, nullable=True)
    quantity = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    loans = relationship("Loan", back_populates="book", cascade="all, delete-orphan")
