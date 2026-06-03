import pytest

@pytest.mark.integration
class TestUsersAPI:
    """Integration tests for the users API endpoints."""

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
