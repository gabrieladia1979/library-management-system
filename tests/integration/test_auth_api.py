import pytest


@pytest.mark.integration
class TestAuthAPI:
    """Integration tests for the authentication API endpoints."""

    def test_login_success(self, client):
        """Test successful login returns a token."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_failure(self, client):
        """Test login with incorrect credentials fails."""
        response = client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username or password"

    def test_protected_endpoint_without_token(self, client):
        """Test accessing a protected endpoint without a token fails."""
        # Use an endpoint that requires authentication
        response = client.get("/api/v1/books/")
        assert response.status_code == 401
        # FastAPI's default OAuth2PasswordBearer returns "Not authenticated" if no token is provided
        # but let's see what the implementation returns.
        # Usually it is {"detail": "Not authenticated"}

    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing a protected endpoint with an invalid token fails."""
        response = client.get(
            "/api/v1/books/",
            headers={"Authorization": "Bearer invalid_token"},
        )
        assert response.status_code == 401
