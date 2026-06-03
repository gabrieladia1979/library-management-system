import pytest
from fastapi import HTTPException

from app.schemas.book import BookCreate, BookUpdate
from app.services import book_service


@pytest.mark.unit
class TestBookService:
    """Unit tests for book service functions."""

    def test_create_book_success(self, db_session):
        book_data = BookCreate(
            title="Test Book", author="Test Author", isbn="1234567890", quantity=2
        )
        book = book_service.create_book(db_session, book_data)
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.isbn == "1234567890"
        assert book.quantity == 2
        assert book.available_copies == 2

    def test_create_book_duplicate_isbn(self, db_session):
        book_data = BookCreate(
            title="Book 1", author="Author", isbn="1234567890", quantity=1
        )
        book_service.create_book(db_session, book_data)
        with pytest.raises(HTTPException) as exc_info:
            book_service.create_book(db_session, book_data)
        assert exc_info.value.status_code == 409

    def test_get_books_all(self, db_session):
        book_service.create_book(
            db_session,
            BookCreate(title="Book A", author="Author A", isbn="1111111111"),
        )
        book_service.create_book(
            db_session,
            BookCreate(title="Book B", author="Author B", isbn="2222222222"),
        )
        books = book_service.get_books(db_session)
        assert len(books) == 2

    def test_get_books_search(self, db_session):
        book_service.create_book(
            db_session,
            BookCreate(title="Python Guide", author="Author A", isbn="1111111111"),
        )
        book_service.create_book(
            db_session,
            BookCreate(title="Java Guide", author="Author B", isbn="2222222222"),
        )
        results = book_service.get_books(db_session, search="Python")
        assert len(results) == 1
        assert results[0].title == "Python Guide"

    def test_get_book_success(self, db_session):
        created = book_service.create_book(
            db_session,
            BookCreate(title="Test", author="Author", isbn="1234567890"),
        )
        book = book_service.get_book(db_session, created.id)
        assert book.id == created.id

    def test_get_book_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            book_service.get_book(db_session, 999)
        assert exc_info.value.status_code == 404

    def test_update_book(self, db_session):
        created = book_service.create_book(
            db_session,
            BookCreate(title="Old Title", author="Author", isbn="1234567890"),
        )
        updated = book_service.update_book(
            db_session, created.id, BookUpdate(title="New Title")
        )
        assert updated.title == "New Title"
        assert updated.author == "Author"  # Unchanged

    def test_delete_book_success(self, db_session):
        created = book_service.create_book(
            db_session,
            BookCreate(title="To Delete", author="Author", isbn="1234567890"),
        )
        book_service.delete_book(db_session, created.id)
        with pytest.raises(HTTPException):
            book_service.get_book(db_session, created.id)
