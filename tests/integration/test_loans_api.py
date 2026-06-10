import pytest


@pytest.mark.integration
class TestLoansAPI:
    """Integration tests for the loans API endpoints."""

    def test_create_loan(self, auth_client, created_book, created_user):
        response = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "active"
        assert data["user_name"] == created_user["name"]
        assert data["book_title"] == created_book["title"]

    def test_create_loan_user_not_found(self, auth_client, created_book):
        response = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": 999, "book_id": created_book["id"]},
        )
        assert response.status_code == 404

    def test_create_loan_book_not_found(self, auth_client, created_user):
        response = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": 999},
        )
        assert response.status_code == 404

    def test_create_loan_no_copies(self, auth_client, created_user):
        book_data = {
            "title": "Rare Book",
            "author": "Author",
            "isbn": "9999999999",
            "quantity": 1,
        }
        book = auth_client.post("/api/v1/books/", json=book_data).json()
        auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": book["id"]},
        )
        # Try to borrow again with a different user
        user2 = auth_client.post(
            "/api/v1/users/", json={"name": "User 2", "email": "u2@email.com"}
        ).json()
        response = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": user2["id"], "book_id": book["id"]},
        )
        assert response.status_code == 409

    def test_return_book(self, auth_client, created_book, created_user):
        loan = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        response = auth_client.put(f"/api/v1/loans/{loan['id']}/return")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "returned"
        assert data["return_date"] is not None

    def test_return_book_already_returned(
        self, auth_client, created_book, created_user
    ):
        loan = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        auth_client.put(f"/api/v1/loans/{loan['id']}/return")
        response = auth_client.put(f"/api/v1/loans/{loan['id']}/return")
        assert response.status_code == 409

    def test_list_loans(self, auth_client, created_book, created_user):
        loan = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        response = auth_client.get("/api/v1/loans/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == loan["id"]
        assert data[0]["user_id"] == created_user["id"]
        assert data[0]["book_id"] == created_book["id"]
        assert data[0]["status"] == "active"
        assert data[0]["user_name"] == created_user["name"]
        assert data[0]["book_title"] == created_book["title"]

    def test_list_loans_filter_status(self, auth_client, created_book, created_user):
        loan = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        auth_client.put(f"/api/v1/loans/{loan['id']}/return")
        active = auth_client.get("/api/v1/loans/?status=active").json()
        returned = auth_client.get("/api/v1/loans/?status=returned").json()
        assert len(active) == 0
        assert len(returned) == 1
        assert returned[0]["id"] == loan["id"]
        assert returned[0]["status"] == "returned"

    def test_list_loans_filter_user_id(self, auth_client, created_book, created_user):
        loan = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        
        # Create user 2 and book 2 to have another loan
        user2 = auth_client.post("/api/v1/users/", json={"name": "User 2", "email": "u2@email.com"}).json()
        book2 = auth_client.post("/api/v1/books/", json={
            "title": "Clean Code II",
            "author": "Robert C. Martin",
            "isbn": "9780132350886",
            "quantity": 2,
        }).json()
        loan2 = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": user2["id"], "book_id": book2["id"]},
        ).json()
        
        response = auth_client.get(f"/api/v1/loans/?user_id={created_user['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == loan["id"]
        assert data[0]["user_id"] == created_user["id"]

    def test_list_loans_filter_book_id(self, auth_client, created_book, created_user):
        loan = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": created_user["id"], "book_id": created_book["id"]},
        ).json()
        
        user2 = auth_client.post("/api/v1/users/", json={"name": "User 2", "email": "u2@email.com"}).json()
        book2 = auth_client.post("/api/v1/books/", json={
            "title": "Clean Code II",
            "author": "Robert C. Martin",
            "isbn": "9780132350886",
            "quantity": 2,
        }).json()
        loan2 = auth_client.post(
            "/api/v1/loans/",
            json={"user_id": user2["id"], "book_id": book2["id"]},
        ).json()
        
        response = auth_client.get(f"/api/v1/loans/?book_id={created_book['id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == loan["id"]
        assert data[0]["book_id"] == created_book["id"]

    def test_check_overdue_endpoint(self, auth_client):
        # We call the post endpoint. It returns a JSON with overdue_count.
        response = auth_client.post("/api/v1/loans/check-overdue")
        assert response.status_code == 200
        assert "overdue_count" in response.json()
