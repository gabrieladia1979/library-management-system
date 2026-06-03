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
