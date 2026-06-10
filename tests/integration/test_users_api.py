import pytest


@pytest.mark.integration
class TestUsersAPI:
    """Integration tests for the users API endpoints."""

    def test_create_user(self, auth_client, sample_user):
        response = auth_client.post("/api/v1/users/", json=sample_user)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_user["name"]
        assert data["email"] == sample_user["email"]
        assert data["is_active"] is True

    def test_create_user_duplicate_email(self, auth_client, sample_user):
        auth_client.post("/api/v1/users/", json=sample_user)
        response = auth_client.post("/api/v1/users/", json=sample_user)
        assert response.status_code == 409

    def test_create_user_invalid_data(self, auth_client):
        response = auth_client.post("/api/v1/users/", json={"name": ""})
        assert response.status_code == 422

    def test_list_users(self, auth_client, sample_user):
        created = auth_client.post("/api/v1/users/", json=sample_user).json()
        response = auth_client.get("/api/v1/users/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == created["id"]
        assert data[0]["name"] == created["name"]
        assert data[0]["email"] == created["email"]

    def test_list_users_search_email(self, auth_client, sample_user):
        u1 = auth_client.post("/api/v1/users/", json=sample_user).json()
        u2 = auth_client.post(
            "/api/v1/users/",
            json={"name": "Alice Smith", "email": "alice@email.com"},
        ).json()
        
        response = auth_client.get("/api/v1/users/?search=alice@email.com")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == u2["id"]
        assert data[0]["email"] == u2["email"]

    def test_get_user(self, auth_client, created_user):
        response = auth_client.get(f"/api/v1/users/{created_user['id']}")
        assert response.status_code == 200
        assert response.json()["name"] == created_user["name"]

    def test_get_user_not_found(self, auth_client):
        response = auth_client.get("/api/v1/users/999")
        assert response.status_code == 404

    def test_update_user(self, auth_client, created_user):
        response = auth_client.put(
            f"/api/v1/users/{created_user['id']}",
            json={"name": "Updated Name"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Name"

    def test_update_user_not_found(self, auth_client):
        response = auth_client.put(
            "/api/v1/users/999",
            json={"name": "New Name"},
        )
        assert response.status_code == 404

    def test_deactivate_user(self, auth_client, created_user):
        response = auth_client.put(f"/api/v1/users/{created_user['id']}/deactivate")
        assert response.status_code == 200
        assert response.json()["is_active"] is False
