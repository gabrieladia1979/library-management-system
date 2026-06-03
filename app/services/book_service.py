from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate


def create_book(db: Session, book_data: BookCreate) -> Book:
    """Create a new book. Raises 409 if ISBN already exists."""
    existing = db.query(Book).filter(Book.isbn == book_data.isbn).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Book with ISBN '{book_data.isbn}' already exists.",
        )
    book = Book(
        **book_data.model_dump(),
        available_copies=book_data.quantity,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


def get_books(
    db: Session,
    search: str | None = None,
    genre: str | None = None,
    available_only: bool = False,
) -> list[Book]:
    """Get all books with optional filters."""
    query = db.query(Book)
    if search:
        query = query.filter(
            (Book.title.ilike(f"%{search}%")) | (Book.author.ilike(f"%{search}%"))
        )
    if genre:
        query = query.filter(Book.genre == genre)
    if available_only:
        query = query.filter(Book.available_copies > 0)
    return query.order_by(Book.title).all()


def get_book(db: Session, book_id: int) -> Book:
    """Get a single book by ID. Raises 404 if not found."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found.",
        )
    return book


def update_book(db: Session, book_id: int, book_data: BookUpdate) -> Book:
    """Update a book partially. Raises 404 if not found."""
    book = get_book(db, book_id)
    update_data = book_data.model_dump(exclude_unset=True)

    if "quantity" in update_data:
        diff = update_data["quantity"] - book.quantity
        book.available_copies = max(0, book.available_copies + diff)

    for field, value in update_data.items():
        setattr(book, field, value)

    db.commit()
    db.refresh(book)
    return book


def delete_book(db: Session, book_id: int) -> None:
    """Delete a book. Raises 409 if it has active loans."""
    book = get_book(db, book_id)
    active_loans = [loan for loan in book.loans if loan.status == "active"]
    if active_loans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete book with active loans.",
        )
    db.delete(book)
    db.commit()
