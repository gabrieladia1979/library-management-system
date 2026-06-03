from datetime import datetime

from pydantic import BaseModel


class LoanCreate(BaseModel):
    user_id: int
    book_id: int


class LoanRead(BaseModel):
    id: int
    user_id: int
    book_id: int
    loan_date: datetime
    due_date: datetime
    return_date: datetime | None
    status: str
    user_name: str | None = None
    book_title: str | None = None

    model_config = {"from_attributes": True}
