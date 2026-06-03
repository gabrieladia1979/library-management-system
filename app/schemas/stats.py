from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_books: int
    total_users: int
    active_loans: int
    overdue_loans: int
    available_books: int
    total_copies: int
