import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.models.book import Book
from app.models.user import User
from app.models.loan import Loan
from app.services import loan_service

@pytest.mark.unit
class TestLoanService:
    """Unit tests for loan service functions."""

    def _create_user(self, db_session, name="Test User", email="test@email.com"):
        user = User(name=name, email=email)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    def _create_book(self, db_session, title="Test Book", isbn="1234567890", quantity=2):
        book = Book(title=title, author="Author", isbn=isbn, quantity=quantity, available_copies=quantity)
        db_session.add(book)
        db_session.commit()
        db_session.refresh(book)
        return book

    def test_borrow_book_success(self, db_session):
        user = self._create_user(db_session)
        book = self._create_book(db_session)
        loan = loan_service.borrow_book(db_session, user.id, book.id)
        assert loan.user_id == user.id
        assert loan.book_id == book.id
        assert loan.status == "active"
        db_session.refresh(book)
        assert book.available_copies == 1

    def test_borrow_book_no_copies(self, db_session):
        user = self._create_user(db_session)
        book = self._create_book(db_session, quantity=1)
        loan_service.borrow_book(db_session, user.id, book.id)
        user2 = self._create_user(db_session, name="User 2", email="user2@email.com")
        with pytest.raises(HTTPException) as exc_info:
            loan_service.borrow_book(db_session, user2.id, book.id)
        assert exc_info.value.status_code == 409
        assert "No copies available" in exc_info.value.detail

    def test_borrow_book_user_not_found(self, db_session):
        book = self._create_book(db_session)
        with pytest.raises(HTTPException) as exc_info:
            loan_service.borrow_book(db_session, 999, book.id)
        assert exc_info.value.status_code == 404

    def test_borrow_book_inactive_user(self, db_session):
        user = self._create_user(db_session)
        user.is_active = False
        db_session.commit()
        book = self._create_book(db_session)
        with pytest.raises(HTTPException) as exc_info:
            loan_service.borrow_book(db_session, user.id, book.id)
        assert exc_info.value.status_code == 409

    def test_borrow_book_already_borrowed(self, db_session):
        user = self._create_user(db_session)
        book = self._create_book(db_session)
        loan_service.borrow_book(db_session, user.id, book.id)
        with pytest.raises(HTTPException) as exc_info:
            loan_service.borrow_book(db_session, user.id, book.id)
        assert exc_info.value.status_code == 409

    def test_return_book_success(self, db_session):
        user = self._create_user(db_session)
        book = self._create_book(db_session, quantity=1)
        loan = loan_service.borrow_book(db_session, user.id, book.id)
        returned = loan_service.return_book(db_session, loan.id)
        assert returned.status == "returned"
        assert returned.return_date is not None
        db_session.refresh(book)
        assert book.available_copies == 1

    def test_return_book_already_returned(self, db_session):
        user = self._create_user(db_session)
        book = self._create_book(db_session)
        loan = loan_service.borrow_book(db_session, user.id, book.id)
        loan_service.return_book(db_session, loan.id)
        with pytest.raises(HTTPException) as exc_info:
            loan_service.return_book(db_session, loan.id)
        assert exc_info.value.status_code == 409

    def test_return_book_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            loan_service.return_book(db_session, 999)
        assert exc_info.value.status_code == 404

    def test_get_loans_filter_by_status(self, db_session):
        user = self._create_user(db_session)
        book1 = self._create_book(db_session, isbn="1111111111")
        book2 = self._create_book(db_session, isbn="2222222222")
        loan1 = loan_service.borrow_book(db_session, user.id, book1.id)
        loan_service.borrow_book(db_session, user.id, book2.id)
        loan_service.return_book(db_session, loan1.id)
        active = loan_service.get_loans(db_session, status_filter="active")
        returned = loan_service.get_loans(db_session, status_filter="returned")
        assert len(active) == 1
        assert len(returned) == 1

    def test_check_overdue_loans(self, db_session):
        user = self._create_user(db_session)
        book = self._create_book(db_session)
        loan = loan_service.borrow_book(db_session, user.id, book.id)
        # Manually set due date to the past
        loan.due_date = datetime.now(timezone.utc) - timedelta(days=1)
        db_session.commit()
        count = loan_service.check_overdue_loans(db_session)
        assert count == 1
        db_session.refresh(loan)
        assert loan.status == "overdue"
