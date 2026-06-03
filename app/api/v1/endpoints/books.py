from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    """Create a new book in the library catalog."""
    return book_service.create_book(db, book)


@router.get("/", response_model=list[BookRead])
def list_books(
    search: str | None = Query(None, description="Search by title or author"),
    genre: str | None = Query(None, description="Filter by genre"),
    available_only: bool = Query(False, description="Show only available books"),
    db: Session = Depends(get_db),
):
    """List all books with optional filters."""
    return book_service.get_books(
        db, search=search, genre=genre, available_only=available_only
    )


@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by ID."""
    return book_service.get_book(db, book_id)


@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    """Update a book's information."""
    return book_service.update_book(db, book_id, book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete a book from the catalog."""
    book_service.delete_book(db, book_id)
