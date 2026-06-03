import pytest


@pytest.mark.system
class TestWorkflows:
    """System tests for end-to-end user workflows."""

    def test_full_borrow_and_return_workflow(self, client):
        """Test the complete lifecycle: create book -> create user -> borrow -> return."""
        # 1. Create a book
        book = client.post(
            "/api/v1/books/",
            json={
                "title": "Test Book",
                "author": "Author",
                "isbn": "1234567890",
                "quantity": 1,
            },
        ).json()
        assert book["available_copies"] == 1

        # 2. Create a user
        user = client.post(
            "/api/v1/users/", json={"name": "Test User", "email": "test@example.com"}
        ).json()

        # 3. Borrow the book
        loan = client.post(
            "/api/v1/loans/", json={"user_id": user["id"], "book_id": book["id"]}
        ).json()
        assert loan["status"] == "active"

        # 4. Verify book is no longer available
        book_updated = client.get(f"/api/v1/books/{book['id']}").json()
        assert book_updated["available_copies"] == 0

        # 5. Try to borrow again (should fail)
        user2 = client.post(
            "/api/v1/users/", json={"name": "User 2", "email": "user2@example.com"}
        ).json()
        response = client.post(
            "/api/v1/loans/", json={"user_id": user2["id"], "book_id": book["id"]}
        )
        assert response.status_code == 409

        # 6. Return the book
        returned = client.put(f"/api/v1/loans/{loan['id']}/return").json()
        assert returned["status"] == "returned"

        # 7. Verify book is available again
        book_final = client.get(f"/api/v1/books/{book['id']}").json()
        assert book_final["available_copies"] == 1

    def test_multiple_users_borrow_same_book(self, client):
        """Test multiple users borrowing copies of the same book."""
        book = client.post(
            "/api/v1/books/",
            json={
                "title": "Popular Book",
                "author": "Author",
                "isbn": "1111111111",
                "quantity": 2,
            },
        ).json()

        user1 = client.post(
            "/api/v1/users/", json={"name": "User 1", "email": "u1@test.com"}
        ).json()
        user2 = client.post(
            "/api/v1/users/", json={"name": "User 2", "email": "u2@test.com"}
        ).json()

        # Both should succeed
        loan1 = client.post(
            "/api/v1/loans/", json={"user_id": user1["id"], "book_id": book["id"]}
        )
        assert loan1.status_code == 201

        loan2 = client.post(
            "/api/v1/loans/", json={"user_id": user2["id"], "book_id": book["id"]}
        )
        assert loan2.status_code == 201

        # Third should fail
        user3 = client.post(
            "/api/v1/users/", json={"name": "User 3", "email": "u3@test.com"}
        ).json()
        response = client.post(
            "/api/v1/loans/", json={"user_id": user3["id"], "book_id": book["id"]}
        )
        assert response.status_code == 409

    def test_dashboard_stats_reflect_operations(self, client):
        """Test that dashboard stats update correctly after operations."""
        # Initial stats
        stats = client.get("/api/v1/stats/dashboard").json()
        assert stats["total_books"] == 0
        assert stats["total_users"] == 0

        # Create data
        book = client.post(
            "/api/v1/books/",
            json={
                "title": "Stats Book",
                "author": "Author",
                "isbn": "3333333333",
                "quantity": 2,
            },
        ).json()
        user = client.post(
            "/api/v1/users/", json={"name": "Stats User", "email": "stats@test.com"}
        ).json()
        client.post(
            "/api/v1/loans/", json={"user_id": user["id"], "book_id": book["id"]}
        )

        # Verify updated stats
        stats = client.get("/api/v1/stats/dashboard").json()
        assert stats["total_books"] == 1
        assert stats["total_users"] == 1
        assert stats["active_loans"] == 1

    def test_cannot_delete_book_with_active_loan(self, client):
        """Test that a book with an active loan cannot be deleted."""
        book = client.post(
            "/api/v1/books/",
            json={
                "title": "Protected Book",
                "author": "Author",
                "isbn": "4444444444",
                "quantity": 1,
            },
        ).json()
        user = client.post(
            "/api/v1/users/", json={"name": "Borrower", "email": "borrower@test.com"}
        ).json()
        loan = client.post(
            "/api/v1/loans/", json={"user_id": user["id"], "book_id": book["id"]}
        ).json()

        # Try to delete — should fail
        response = client.delete(f"/api/v1/books/{book['id']}")
        assert response.status_code == 409

        # Return book, then delete — should succeed
        client.put(f"/api/v1/loans/{loan['id']}/return")
        response = client.delete(f"/api/v1/books/{book['id']}")
        assert response.status_code == 204

    def test_deactivate_user_with_active_loan_fails(self, client):
        """Test that a user with active loans cannot be deactivated."""
        book = client.post(
            "/api/v1/books/",
            json={
                "title": "Book",
                "author": "Author",
                "isbn": "5555555555",
                "quantity": 1,
            },
        ).json()
        user = client.post(
            "/api/v1/users/", json={"name": "Active User", "email": "active@test.com"}
        ).json()
        client.post(
            "/api/v1/loans/", json={"user_id": user["id"], "book_id": book["id"]}
        )

        response = client.put(f"/api/v1/users/{user['id']}/deactivate")
        assert response.status_code == 409
