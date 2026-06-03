from datetime import datetime

from pydantic import BaseModel, Field

class BookCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    author: str = Field(..., min_length=1, max_length=150)
    isbn: str = Field(..., min_length=10, max_length=13)
    genre: str | None = None
    published_year: int | None = None
    quantity: int = Field(default=1, ge=1)
    description: str | None = None

class BookRead(BaseModel):
    id: int
    title: str
    author: str
    isbn: str
    genre: str | None
    published_year: int | None
    quantity: int
    available_copies: int
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=150)
    genre: str | None = None
    published_year: int | None = None
    quantity: int | None = Field(default=None, ge=1)
    description: str | None = None
