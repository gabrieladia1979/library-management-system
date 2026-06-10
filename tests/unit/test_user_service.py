import pytest
from fastapi import HTTPException

from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service


@pytest.mark.unit
class TestUserService:
    """Unit tests for user service functions."""

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
        u1 = user_service.create_user(
            db_session, UserCreate(name="User A", email="a@email.com")
        )
        u2 = user_service.create_user(
            db_session, UserCreate(name="User B", email="b@email.com")
        )
        users = user_service.get_users(db_session)
        assert len(users) == 2
        assert users[0].id == u1.id
        assert users[0].name == "User A"
        assert users[1].id == u2.id
        assert users[1].name == "User B"

    def test_get_users_search(self, db_session):
        u1 = user_service.create_user(
            db_session, UserCreate(name="Alice Smith", email="alice@email.com")
        )
        u2 = user_service.create_user(
            db_session, UserCreate(name="Bob Jones", email="bob@email.com")
        )
        results = user_service.get_users(db_session, search="Alice")
        assert len(results) == 1
        assert results[0].id == u1.id
        assert results[0].name == "Alice Smith"

    def test_get_users_search_email(self, db_session):
        u1 = user_service.create_user(
            db_session, UserCreate(name="Alice Smith", email="alice@email.com")
        )
        u2 = user_service.create_user(
            db_session, UserCreate(name="Bob Jones", email="bob@email.com")
        )
        results = user_service.get_users(db_session, search="bob@email.com")
        assert len(results) == 1
        assert results[0].id == u2.id
        assert results[0].email == "bob@email.com"

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

    def test_update_user_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            user_service.update_user(
                db_session, 999, UserUpdate(name="New Name")
            )
        assert exc_info.value.status_code == 404

    def test_deactivate_user_success(self, db_session):
        user = user_service.create_user(
            db_session, UserCreate(name="Test User", email="test@email.com")
        )
        assert user.is_active is True
        deactivated = user_service.deactivate_user(db_session, user.id)
        assert deactivated.is_active is False

    def test_deactivate_user_with_active_loans_fails(self, db_session):
        from app.models.book import Book
        from app.services import loan_service
        
        user = user_service.create_user(
            db_session, UserCreate(name="Test User", email="test@email.com")
        )
        book = Book(
            title="Test Book",
            author="Author",
            isbn="1234567890",
            quantity=1,
            available_copies=1,
        )
        db_session.add(book)
        db_session.commit()
        db_session.refresh(book)
        
        loan_service.borrow_book(db_session, user.id, book.id)
        
        with pytest.raises(HTTPException) as exc_info:
            user_service.deactivate_user(db_session, user.id)
        assert exc_info.value.status_code == 409
        assert "Cannot deactivate user with active loans" in exc_info.value.detail
