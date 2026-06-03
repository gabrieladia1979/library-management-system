from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.loan import Loan
from app.schemas.loan import LoanCreate, LoanRead
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["loans"])


def _loan_to_read(loan: Loan) -> LoanRead:
    """Convert Loan model to LoanRead schema with expanded names."""
    return LoanRead(
        id=loan.id,
        user_id=loan.user_id,
        book_id=loan.book_id,
        loan_date=loan.loan_date,
        due_date=loan.due_date,
        return_date=loan.return_date,
        status=loan.status,
        user_name=loan.user.name if loan.user else None,
        book_title=loan.book.title if loan.book else None,
    )


@router.post("/", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    """Borrow a book from the library."""
    result = loan_service.borrow_book(db, loan.user_id, loan.book_id)
    return _loan_to_read(result)


@router.get("/", response_model=list[LoanRead])
def list_loans(
    status: str | None = Query(
        None, description="Filter by status: active, returned, overdue"
    ),
    user_id: int | None = Query(None, description="Filter by user ID"),
    book_id: int | None = Query(None, description="Filter by book ID"),
    db: Session = Depends(get_db),
):
    """List all loans with optional filters."""
    loans = loan_service.get_loans(
        db, status_filter=status, user_id=user_id, book_id=book_id
    )
    return [_loan_to_read(loan) for loan in loans]


@router.put("/{loan_id}/return", response_model=LoanRead)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    """Return a borrowed book."""
    result = loan_service.return_book(db, loan_id)
    return _loan_to_read(result)


@router.post("/check-overdue")
def check_overdue(db: Session = Depends(get_db)):
    """Check and update overdue loans."""
    count = loan_service.check_overdue_loans(db)
    return {"overdue_count": count}
