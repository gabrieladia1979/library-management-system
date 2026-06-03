import os

BASE_DIR = r"C:\Users\gabri\.gemini\antigravity\scratch\library-management-system"

FILES = {
    "tests/conftest.py": """import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db.dependencies import get_db
from app.main import app

# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    \"\"\"Create a fresh database session for each test.\"\"\"
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    \"\"\"FastAPI TestClient with overridden DB dependency.\"\"\"
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def sample_book():
    \"\"\"Sample book data for tests.\"\"\"
    return {
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "isbn": "9780132350884",
        "genre": "Software",
        "quantity": 3,
        "published_year": 2008,
        "description": "A handbook of agile software craftsmanship.",
    }

@pytest.fixture
def sample_user():
    \"\"\"Sample user data for tests.\"\"\"
    return {
        "name": "María González",
        "email": "maria.gonzalez@email.com",
    }

@pytest.fixture
def created_book(client, sample_book):
    \"\"\"Create and return a book via API.\"\"\"
    response = client.post("/api/v1/books/", json=sample_book)
    return response.json()

@pytest.fixture
def created_user(client, sample_user):
    \"\"\"Create and return a user via API.\"\"\"
    response = client.post("/api/v1/users/", json=sample_user)
    return response.json()
""",
    "tests/unit/test_book_service.py": """import pytest
from fastapi import HTTPException

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate
from app.services import book_service

@pytest.mark.unit
class TestBookService:
    \"\"\"Unit tests for book service functions.\"\"\"

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
""",
    "tests/unit/test_user_service.py": """import pytest
from fastapi import HTTPException

from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service

@pytest.mark.unit
class TestUserService:
    \"\"\"Unit tests for user service functions.\"\"\"

    def test_create_user_success(self, db_session):
        user_data = UserCreate(name="Test User", email="test@email.com")
        user = user_service.create_user(db_session, user_data)
        assert user.name == "Test User"
        assert user.email == "test@email.com"
        assert user.is_active is True

    def test_create_user_duplicate_email(self, db_session):
        user_data = UserCreate(name="User 1", email="test@email.com")
        user_service.create_user(db_session, user_data)
        with pytest.raises(HTTPException) as exc_info:
            user_service.create_user(db_session, user_data)
        assert exc_info.value.status_code == 409

    def test_get_users_all(self, db_session):
        user_service.create_user(
            db_session, UserCreate(name="User A", email="a@email.com")
        )
        user_service.create_user(
            db_session, UserCreate(name="User B", email="b@email.com")
        )
        users = user_service.get_users(db_session)
        assert len(users) == 2

    def test_get_users_search(self, db_session):
        user_service.create_user(
            db_session, UserCreate(name="Alice Smith", email="alice@email.com")
        )
        user_service.create_user(
            db_session, UserCreate(name="Bob Jones", email="bob@email.com")
        )
        results = user_service.get_users(db_session, search="Alice")
        assert len(results) == 1

    def test_get_user_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            user_service.get_user(db_session, 999)
        assert exc_info.value.status_code == 404

    def test_update_user(self, db_session):
        created = user_service.create_user(
            db_session, UserCreate(name="Old Name", email="test@email.com")
        )
        updated = user_service.update_user(
            db_session, created.id, UserUpdate(name="New Name")
        )
        assert updated.name == "New Name"
        assert updated.email == "test@email.com"  # Unchanged
""",
    "tests/unit/test_loan_service.py": """import pytest
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException

from app.models.book import Book
from app.models.user import User
from app.models.loan import Loan
from app.services import loan_service

@pytest.mark.unit
class TestLoanService:
    \"\"\"Unit tests for loan service functions.\"\"\"

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
""",
    "tests/integration/test_books_api.py": """import pytest

@pytest.mark.integration
class TestBooksAPI:
    \"\"\"Integration tests for the books API endpoints.\"\"\"

    def test_create_book(self, client, sample_book):
        response = client.post("/api/v1/books/", json=sample_book)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_book["title"]
        assert data["isbn"] == sample_book["isbn"]
        assert data["available_copies"] == sample_book["quantity"]
        assert "id" in data

    def test_create_book_duplicate_isbn(self, client, sample_book):
        client.post("/api/v1/books/", json=sample_book)
        response = client.post("/api/v1/books/", json=sample_book)
        assert response.status_code == 409

    def test_create_book_invalid_data(self, client):
        response = client.post("/api/v1/books/", json={"title": ""})
        assert response.status_code == 422

    def test_list_books(self, client, sample_book):
        client.post("/api/v1/books/", json=sample_book)
        response = client.get("/api/v1/books/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_books_search(self, client, sample_book):
        client.post("/api/v1/books/", json=sample_book)
        response = client.get("/api/v1/books/?search=Clean")
        assert response.status_code == 200
        assert len(response.json()) == 1
        response = client.get("/api/v1/books/?search=Nonexistent")
        assert len(response.json()) == 0

    def test_get_book(self, client, created_book):
        response = client.get(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == created_book["title"]

    def test_get_book_not_found(self, client):
        response = client.get("/api/v1/books/999")
        assert response.status_code == 404

    def test_update_book(self, client, created_book):
        response = client.put(
            f"/api/v1/books/{created_book['id']}",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_delete_book(self, client, created_book):
        response = client.delete(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 204
        response = client.get(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 404
""",
    "tests/integration/test_users_api.py": """import pytest

@pytest.mark.integration
class TestUsersAPI:
    \"\"\"Integration tests for the users API endpoints.\"\"\"

    def test_create_user(self, client, sample_user):
        response = client.post("/api/v1/users/", json=sample_user)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_user["name"]
        assert data["email"] == sample_user["email"]
        assert data["is_active"] is True

    def test_create_user_duplicate_email(self, client, sample_user):
        client.post("/api/v1/users/", json=sample_user)
        response = client.post("/api/v1/users/", json=sample_user)
        assert response.status_code == 409

    def test_create_user_invalid_data(self, client):
        response = client.post("/api/v1/users/", json={"name": ""})
        assert response.status_code == 422

    def test_list_users(self, client, sample_user):
        client.post("/api/v1/users/", json=sample_user)
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_get_user(self, client, created_user):
        response = client.get(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == created_user["name"]

    def test_get_user_not_found(self, client):
        response = client.get("/api/v1/users/999")
        assert response.status_code == 404

    def test_update_user(self, client, created_user):
        response = client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_deactivate_user(self, client, created_user):
        response = client.put(f"/api/v1/users/{created_user['id']}/deactivate")
        assert response.status_code == 200
        assert response.json()["is_active"] is False
""",
    "tests/integration/test_loans_api.py": """import pytest

@pytest.mark.integration
class TestLoansAPI:
    \"\"\"Integration tests for the loans API endpoints.\"\"\"

    def test_create_loan(self, client, created_book, created_user):
        response = client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"
        assert data["user_name"] == created_user["name"]
        assert data["book_title"] == created_book["title"]

    def test_create_loan_user_not_found(self, client, created_book):
        response = client.post(
            "/api/v1/loans/",
            json={"user_id": 999, "book_id": created_book["id"]},
        )
        assert response.status_code == 404

    def test_create_loan_book_not_found(self, client, created_user):
        response = client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": 999},
        )
        assert response.status_code == 404

    def test_create_loan_no_copies(self, client, created_user):
        book_data = {
            "title": "Rare Book",
            "author": "Author",
            "isbn": "9999999999",
            "quantity": 1,
        }
        book = client.post("/api/v1/books/", json=book_data).json()
        client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": book["id"]},
        )
        # Try to borrow again with a different user
        user2 = client.post(
            "/api/v1/users/", json={"name": "User 2", "email": "u2@email.com"}
        ).json()
        response = client.post(
            "/api/v1/loans/",
            json={"user_id": user2["id"], "book_id": book["id"]},
        )
        assert response.status_code == 409

    def test_return_book(self, client, created_book, created_user):
        loan = client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        response = client.put(f"/api/v1/loans/{loan['id']}/return")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "returned"
        assert data["return_date"] is not None

    def test_return_book_already_returned(self, client, created_book, created_user):
        loan = client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        client.put(f"/api/v1/loans/{loan['id']}/return")
        response = client.put(f"/api/v1/loans/{loan['id']}/return")
        assert response.status_code == 409

    def test_list_loans(self, client, created_book, created_user):
        client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        )
        response = client.get("/api/v1/loans/")
        assert response.status_code == 200
        assert len(response.json()) == 1

    def test_list_loans_filter_status(self, client, created_book, created_user):
        loan = client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        client.put(f"/api/v1/loans/{loan['id']}/return")
        active = client.get("/api/v1/loans/?status=active").json()
        returned = client.get("/api/v1/loans/?status=returned").json()
        assert len(active) == 0
        assert len(returned) == 1
""",
    "tests/system/test_workflows.py": """import pytest

@pytest.mark.system
class TestWorkflows:
    \"\"\"System tests for end-to-end user workflows.\"\"\"

    def test_full_borrow_and_return_workflow(self, client):
        \"\"\"Test the complete lifecycle: create book -> create user -> borrow -> return.\"\"\"
        # 1. Create a book
        book = client.post("/api/v1/books/", json={
            "title": "Test Book", "author": "Author", "isbn": "1234567890", "quantity": 1
        }).json()
        assert book["available_copies"] == 1

        # 2. Create a user
        user = client.post("/api/v1/users/", json={
            "name": "Test User", "email": "test@example.com"
        }).json()

        # 3. Borrow the book
        loan = client.post("/api/v1/loans/", json={
            "user_id": user["id"], "book_id": book["id"]
        }).json()
        assert loan["status"] == "active"

        # 4. Verify book is no longer available
        book_updated = client.get(f"/api/v1/books/{book['id']}").json()
        assert book_updated["available_copies"] == 0

        # 5. Try to borrow again (should fail)
        user2 = client.post("/api/v1/users/", json={
            "name": "User 2", "email": "user2@example.com"
        }).json()
        response = client.post("/api/v1/loans/", json={
            "user_id": user2["id"], "book_id": book["id"]
        })
        assert response.status_code == 409

        # 6. Return the book
        returned = client.put(f"/api/v1/loans/{loan['id']}/return").json()
        assert returned["status"] == "returned"

        # 7. Verify book is available again
        book_final = client.get(f"/api/v1/books/{book['id']}").json()
        assert book_final["available_copies"] == 1

    def test_multiple_users_borrow_same_book(self, client):
        \"\"\"Test multiple users borrowing copies of the same book.\"\"\"
        book = client.post("/api/v1/books/", json={
            "title": "Popular Book", "author": "Author", "isbn": "1111111111", "quantity": 2
        }).json()

        user1 = client.post("/api/v1/users/", json={
            "name": "User 1", "email": "u1@test.com"
        }).json()
        user2 = client.post("/api/v1/users/", json={
            "name": "User 2", "email": "u2@test.com"
        }).json()

        # Both should succeed
        loan1 = client.post("/api/v1/loans/", json={
            "user_id": user1["id"], "book_id": book["id"]
        })
        assert loan1.status_code == 201

        loan2 = client.post("/api/v1/loans/", json={
            "user_id": user2["id"], "book_id": book["id"]
        })
        assert loan2.status_code == 201

        # Third should fail
        user3 = client.post("/api/v1/users/", json={
            "name": "User 3", "email": "u3@test.com"
        }).json()
        response = client.post("/api/v1/loans/", json={
            "user_id": user3["id"], "book_id": book["id"]
        })
        assert response.status_code == 409

    def test_dashboard_stats_reflect_operations(self, client):
        \"\"\"Test that dashboard stats update correctly after operations.\"\"\"
        # Initial stats
        stats = client.get("/api/v1/stats/dashboard").json()
        assert stats["total_books"] == 0
        assert stats["total_users"] == 0

        # Create data
        book = client.post("/api/v1/books/", json={
            "title": "Stats Book", "author": "Author", "isbn": "3333333333", "quantity": 2
        }).json()
        user = client.post("/api/v1/users/", json={
            "name": "Stats User", "email": "stats@test.com"
        }).json()
        client.post("/api/v1/loans/", json={
            "user_id": user["id"], "book_id": book["id"]
        })

        # Verify updated stats
        stats = client.get("/api/v1/stats/dashboard").json()
        assert stats["total_books"] == 1
        assert stats["total_users"] == 1
        assert stats["active_loans"] == 1

    def test_cannot_delete_book_with_active_loan(self, client):
        \"\"\"Test that a book with an active loan cannot be deleted.\"\"\"
        book = client.post("/api/v1/books/", json={
            "title": "Protected Book", "author": "Author", "isbn": "4444444444", "quantity": 1
        }).json()
        user = client.post("/api/v1/users/", json={
            "name": "Borrower", "email": "borrower@test.com"
        }).json()
        loan = client.post("/api/v1/loans/", json={
            "user_id": user["id"], "book_id": book["id"]
        }).json()

        # Try to delete — should fail
        response = client.delete(f"/api/v1/books/{book['id']}")
        assert response.status_code == 409

        # Return book, then delete — should succeed
        client.put(f"/api/v1/loans/{loan['id']}/return")
        response = client.delete(f"/api/v1/books/{book['id']}")
        assert response.status_code == 204

    def test_deactivate_user_with_active_loan_fails(self, client):
        \"\"\"Test that a user with active loans cannot be deactivated.\"\"\"
        book = client.post("/api/v1/books/", json={
            "title": "Book", "author": "Author", "isbn": "5555555555", "quantity": 1
        }).json()
        user = client.post("/api/v1/users/", json={
            "name": "Active User", "email": "active@test.com"
        }).json()
        client.post("/api/v1/loans/", json={
            "user_id": user["id"], "book_id": book["id"]
        })

        response = client.put(f"/api/v1/users/{user['id']}/deactivate")
        assert response.status_code == 409
"""
}

for rel_path, content in FILES.items():
    full_path = os.path.join(BASE_DIR, rel_path.replace("/", "\\"))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Generated test files!")
