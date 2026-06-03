from datetime import UTC, datetime, timedelta

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    loan_date = Column(DateTime, default=lambda: datetime.now(UTC))
    due_date = Column(
        DateTime, default=lambda: datetime.now(UTC) + timedelta(days=14)
    )
    return_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")  # active, returned, overdue

    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")
