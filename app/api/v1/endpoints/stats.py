from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.book import Book
from app.models.loan import Loan
from app.models.user import User
from app.schemas.stats import DashboardStats

router = APIRouter(prefix="/stats", tags=["statistics"])

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics."""
    total_books = db.query(func.count(Book.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_loans = (
        db.query(func.count(Loan.id)).filter(Loan.status == "active").scalar() or 0
    )
    overdue_loans = (
        db.query(func.count(Loan.id)).filter(Loan.status == "overdue").scalar() or 0
    )
    available_books = (
        db.query(func.count(Book.id)).filter(Book.available_copies > 0).scalar() or 0
    )
    total_copies = db.query(func.sum(Book.quantity)).scalar() or 0

    return DashboardStats(
        total_books=total_books,
        total_users=total_users,
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        available_books=available_books,
        total_copies=total_copies,
    )
