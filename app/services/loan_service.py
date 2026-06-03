from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.loan import Loan
from app.models.user import User

def borrow_book(db: Session, user_id: int, book_id: int) -> Loan:
    """Create a new loan. Validates user exists, book exists, and copies available."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot borrow books for inactive user.",
        )

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found.",
        )
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No copies available for this book.",
        )

    # Check if user already has this book borrowed
    existing_loan = (
        db.query(Loan)
        .filter(
            Loan.user_id == user_id,
            Loan.book_id == book_id,
            Loan.status == "active",
        )
        .first()
    )
    if existing_loan:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has an active loan for this book.",
        )

    loan = Loan(user_id=user_id, book_id=book_id)
    book.available_copies -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

def return_book(db: Session, loan_id: int) -> Loan:
    """Return a borrowed book. Raises 404/409 if loan not found or already returned."""
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan with ID {loan_id} not found.",
        )
    if loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This book has already been returned.",
        )

    loan.status = "returned"
    loan.return_date = datetime.now(timezone.utc)
    loan.book.available_copies += 1
    db.commit()
    db.refresh(loan)
    return loan

def get_loans(
    db: Session,
    status_filter: str | None = None,
    user_id: int | None = None,
    book_id: int | None = None,
) -> list[Loan]:
    """Get all loans with optional filters."""
    query = db.query(Loan)
    if status_filter:
        query = query.filter(Loan.status == status_filter)
    if user_id:
        query = query.filter(Loan.user_id == user_id)
    if book_id:
        query = query.filter(Loan.book_id == book_id)
    return query.order_by(Loan.loan_date.desc()).all()

def check_overdue_loans(db: Session) -> int:
    """Update status of overdue loans. Returns count of newly overdue loans."""
    now = datetime.now(timezone.utc)
    overdue_loans = (
        db.query(Loan)
        .filter(Loan.status == "active", Loan.due_date < now)
        .all()
    )
    for loan in overdue_loans:
        loan.status = "overdue"
    db.commit()
    return len(overdue_loans)
