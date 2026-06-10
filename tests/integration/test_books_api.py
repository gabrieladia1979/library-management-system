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
        created = auth_client.post("/api/v1/books/", json=sample_book).json()
        response = auth_client.get("/api/v1/books/?search=Clean")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == created["id"]
        assert data[0]["title"] == created["title"]
        assert data[0]["isbn"] == created["isbn"]

        response = auth_client.get("/api/v1/books/?search=Nonexistent")
        assert len(response.json()) == 0

    def test_list_books_filter_genre(self, auth_client, sample_book):
        auth_client.post("/api/v1/books/", json=sample_book).json()
        b2_data = sample_book.copy()
        b2_data["title"] = "Refactoring"
        b2_data["isbn"] = "9780201485677"
        b2_data["genre"] = "Refactoring"
        b2 = auth_client.post("/api/v1/books/", json=b2_data).json()

        response = auth_client.get(f"/api/v1/books/?genre={b2['genre']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == b2["id"]
        assert data[0]["genre"] == b2["genre"]

    def test_list_books_filter_available_only(self, auth_client, sample_book):
        b1 = auth_client.post("/api/v1/books/", json=sample_book).json()
        # Create a book with quantity 1 and then borrow it to make availability 0
        b2_data = sample_book.copy()
        b2_data["title"] = "No copies book"
        b2_data["isbn"] = "9780132350885"
        b2_data["quantity"] = 1
        b2 = auth_client.post("/api/v1/books/", json=b2_data).json()

        user = auth_client.post(
            "/api/v1/users/", json={"name": "User 1", "email": "u1@email.com"}
        ).json()
        auth_client.post(
            "/api/v1/loans/", json={"user_id": user["id"], "book_id": b2["id"]}
        )

        response = auth_client.get("/api/v1/books/?available_only=true")
        assert response.status_code == 200
        data = response.json()
        # b2 has 0 available copies now, so only b1 and any other previously created available books should be returned
        available_ids = [b["id"] for b in data]
        assert b2["id"] not in available_ids
        assert b1["id"] in available_ids

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

    def test_update_book_not_found(self, auth_client):
        response = auth_client.put(
            "/api/v1/books/999",
            json={"title": "New Title"},
        )
        assert response.status_code == 404

    def test_delete_book(self, auth_client, created_book):
        response = auth_client.delete(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 204
        response = auth_client.get(f"/api/v1/books/{created_book['id']}")
        assert response.status_code == 404
