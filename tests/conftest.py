import pytest
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
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden DB dependency."""

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
    """Sample book data for tests."""
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
    """Sample user data for tests."""
    return {
        "name": "María González",
        "email": "maria.gonzalez@email.com",
    }


@pytest.fixture(scope="function")
def auth_token(client):
    """Get a valid JWT token for tests."""
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function")
def auth_client(client, auth_token):
    """Client with Authorization header."""
    client.headers = {**client.headers, "Authorization": f"Bearer {auth_token}"}
    return client


@pytest.fixture
def created_book(auth_client, sample_book):
    """Create and return a book via API."""
    response = auth_client.post("/api/v1/books/", json=sample_book)
    return response.json()


@pytest.fixture
def created_user(auth_client, sample_user):
    """Create and return a user via API."""
    response = auth_client.post("/api/v1/users/", json=sample_user)
    return response.json()
