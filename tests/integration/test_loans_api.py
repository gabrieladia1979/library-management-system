import pytest

@pytest.mark.integration
class TestLoansAPI:
    """Integration tests for the loans API endpoints."""

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
