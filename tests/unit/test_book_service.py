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
        b1 = book_service.create_book(
            db_session,
            BookCreate(title="Book A", author="Author A", isbn="1111111111"),
        )
        b2 = book_service.create_book(
            db_session,
            BookCreate(title="Book B", author="Author B", isbn="2222222222"),
        )
        books = book_service.get_books(db_session)
        assert len(books) == 2
        assert books[0].id == b1.id
        assert books[0].title == "Book A"
        assert books[1].id == b2.id
        assert books[1].title == "Book B"

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

    def test_get_books_filter_genre(self, db_session):
        book_service.create_book(
            db_session,
            BookCreate(
                title="Book 1", author="Author A", isbn="1111111111", genre="Sci-Fi"
            ),
        )
        book_service.create_book(
            db_session,
            BookCreate(
                title="Book 2", author="Author B", isbn="2222222222", genre="Fantasy"
            ),
        )
        results = book_service.get_books(db_session, genre="Sci-Fi")
        assert len(results) == 1
        assert results[0].title == "Book 1"
        assert results[0].genre == "Sci-Fi"

    def test_get_books_filter_available_only(self, db_session):
        b1 = book_service.create_book(
            db_session,
            BookCreate(
                title="Book 1", author="Author A", isbn="1111111111", quantity=1
            ),
        )
        b1.available_copies = 0
        db_session.commit()
        b2 = book_service.create_book(
            db_session,
            BookCreate(
                title="Book 2", author="Author B", isbn="2222222222", quantity=2
            ),
        )
        results = book_service.get_books(db_session, available_only=True)
        assert len(results) == 1
        assert results[0].id == b2.id
        assert results[0].available_copies == 2

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

    def test_update_book_quantity(self, db_session):
        created = book_service.create_book(
            db_session,
            BookCreate(
                title="Test Book", author="Author", isbn="1234567890", quantity=2
            ),
        )
        assert created.quantity == 2
        assert created.available_copies == 2

        # Increase quantity
        updated = book_service.update_book(
            db_session, created.id, BookUpdate(quantity=5)
        )
        assert updated.quantity == 5
        assert updated.available_copies == 5

        # Decrease quantity
        updated2 = book_service.update_book(
            db_session, created.id, BookUpdate(quantity=3)
        )
        assert updated2.quantity == 3
        assert updated2.available_copies == 3

    def test_update_book_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            book_service.update_book(db_session, 999, BookUpdate(title="New Title"))
        assert exc_info.value.status_code == 404

    def test_delete_book_success(self, db_session):
        created = book_service.create_book(
            db_session,
            BookCreate(title="To Delete", author="Author", isbn="1234567890"),
        )
        book_service.delete_book(db_session, created.id)
        with pytest.raises(HTTPException):
            book_service.get_book(db_session, created.id)
