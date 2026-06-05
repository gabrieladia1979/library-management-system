import pytest


@pytest.mark.integration
class TestBooksAPI:
    """Integration tests for the books API endpoints."""

    def test_create_book(self, auth_client, sample_book):
        response = auth_client.post("/api/v1/books/", json=sample_book)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == sample_book["title"]
        assert data["isbn"] == sample_book["isbn"]
        assert data["available_copies"] == sample_book["quantity"]
        assert "id" in data

    def test_create_book_duplicate_isbn(self, auth_client, sample_book):
        auth_client.post("/api/v1/books/", json=sample_book)
        response = auth_client.post("/api/v1/books/", json=sample_book)
        assert response.status_code == 409

    def test_create_book_invalid_data(self, auth_client):
        response = auth_client.post("/api/v1/books/", json={"title": ""})
        assert response.status_code == 422

    def test_list_books(self, auth_client, sample_book):
        auth_client.post("/api/v1/books/", json=sample_book)
        response = auth_client.get("/api/v1/books/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_books_search(self, auth_client, sample_book):
        auth_client.post("/api/v1/books/", json=sample_book)
        response = auth_client.get("/api/v1/books/?search=Clean")
        assert response.status_code == 200
        assert len(response.json()) == 1
        response = auth_client.get("/api/v1/books/?search=Nonexistent")
        assert len(response.json()) == 0

    def test_get_book(self, auth_client, created_book):
        response = auth_client.get(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 200
        assert response.json()["title"] == created_book["title"]

    def test_get_book_not_found(self, auth_client):
        response = auth_client.get("/api/v1/books/999")
        assert response.status_code == 404

    def test_update_book(self, auth_client, created_book):
        response = auth_client.put(
            f"/api/v1/books/{created_book['id']}",
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200
        assert response.json()["title"] == "Updated Title"

    def test_delete_book(self, auth_client, created_book):
        response = auth_client.delete(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 204
        response = auth_client.get(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 404
