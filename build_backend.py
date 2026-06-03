import os

BASE_DIR = r"C:\Users\gabri\.gemini\antigravity\scratch\library-management-system"

FILES = {
    "app/__init__.py": "",
    "app/core/__init__.py": "",
    "app/db/__init__.py": "",
    "app/models/__init__.py": "",
    "app/schemas/__init__.py": "",
    "app/api/__init__.py": "",
    "app/api/v1/__init__.py": "",
    "app/api/v1/endpoints/__init__.py": "",
    "app/services/__init__.py": "",
    "tests/__init__.py": "",
    "tests/unit/__init__.py": "",
    "tests/integration/__init__.py": "",
    "tests/system/__init__.py": "",

    "app/core/config.py": """from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "BiblioTech"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./library.db"
    API_V1_STR: str = "/api/v1"

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()
""",
    "app/db/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass
""",
    "app/db/dependencies.py": """from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""",
    "app/models/book.py": """from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base

class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    author = Column(String(150), nullable=False)
    isbn = Column(String(13), unique=True, nullable=False, index=True)
    genre = Column(String(50), nullable=True)
    published_year = Column(Integer, nullable=True)
    quantity = Column(Integer, default=1)
    available_copies = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    loans = relationship("Loan", back_populates="book")
""",
    "app/models/user.py": """from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    loans = relationship("Loan", back_populates="user")
""",
    "app/models/loan.py": """from datetime import datetime, timedelta, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    loan_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(
        DateTime, default=lambda: datetime.now(timezone.utc) + timedelta(days=14)
    )
    return_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="active")  # active, returned, overdue

    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")
""",
    "app/schemas/book.py": """from datetime import datetime

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
""",
    "app/schemas/user.py": """from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=150)

class UserRead(BaseModel):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, min_length=5, max_length=150)
    is_active: bool | None = None
""",
    "app/schemas/loan.py": """from datetime import datetime

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
""",
    "app/schemas/stats.py": """from pydantic import BaseModel

class DashboardStats(BaseModel):
    total_books: int
    total_users: int
    active_loans: int
    overdue_loans: int
    available_books: int
    total_copies: int
""",
    "app/services/book_service.py": """from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.schemas.book import BookCreate, BookUpdate

def create_book(db: Session, book_data: BookCreate) -> Book:
    \"\"\"Create a new book. Raises 409 if ISBN already exists.\"\"\"
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
    \"\"\"Get all books with optional filters.\"\"\"
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
    \"\"\"Get a single book by ID. Raises 404 if not found.\"\"\"
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found.",
        )
    return book

def update_book(db: Session, book_id: int, book_data: BookUpdate) -> Book:
    \"\"\"Update a book partially. Raises 404 if not found.\"\"\"
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
    \"\"\"Delete a book. Raises 409 if it has active loans.\"\"\"
    book = get_book(db, book_id)
    active_loans = [l for l in book.loans if l.status == "active"]
    if active_loans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete book with active loans.",
        )
    db.delete(book)
    db.commit()
""",
    "app/services/user_service.py": """from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

def create_user(db: Session, user_data: UserCreate) -> User:
    \"\"\"Create a new user. Raises 409 if email already exists.\"\"\"
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_data.email}' already exists.",
        )
    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_users(db: Session, search: str | None = None) -> list[User]:
    \"\"\"Get all users with optional search filter.\"\"\"
    query = db.query(User)
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )
    return query.order_by(User.name).all()

def get_user(db: Session, user_id: int) -> User:
    \"\"\"Get a single user by ID. Raises 404 if not found.\"\"\"
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user

def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    \"\"\"Update a user partially. Raises 404 if not found.\"\"\"
    user = get_user(db, user_id)
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user

def deactivate_user(db: Session, user_id: int) -> User:
    \"\"\"Deactivate a user. Raises 409 if user has active loans.\"\"\"
    user = get_user(db, user_id)
    active_loans = [l for l in user.loans if l.status == "active"]
    if active_loans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate user with active loans.",
        )
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
""",
    "app/services/loan_service.py": """from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.book import Book
from app.models.loan import Loan
from app.models.user import User

def borrow_book(db: Session, user_id: int, book_id: int) -> Loan:
    \"\"\"Create a new loan. Validates user exists, book exists, and copies available.\"\"\"
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot borrow books for inactive user.",
        )

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found.",
        )
    if book.available_copies <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No copies available for this book.",
        )

    # Check if user already has this book borrowed
    existing_loan = (
        db.query(Loan)
        .filter(
            Loan.user_id == user_id,
            Loan.book_id == book_id,
            Loan.status == "active",
        )
        .first()
    )
    if existing_loan:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has an active loan for this book.",
        )

    loan = Loan(user_id=user_id, book_id=book_id)
    book.available_copies -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

def return_book(db: Session, loan_id: int) -> Loan:
    \"\"\"Return a borrowed book. Raises 404/409 if loan not found or already returned.\"\"\"
    loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan with ID {loan_id} not found.",
        )
    if loan.status == "returned":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This book has already been returned.",
        )

    loan.status = "returned"
    loan.return_date = datetime.now(timezone.utc)
    loan.book.available_copies += 1
    db.commit()
    db.refresh(loan)
    return loan

def get_loans(
    db: Session,
    status_filter: str | None = None,
    user_id: int | None = None,
    book_id: int | None = None,
) -> list[Loan]:
    \"\"\"Get all loans with optional filters.\"\"\"
    query = db.query(Loan)
    if status_filter:
        query = query.filter(Loan.status == status_filter)
    if user_id:
        query = query.filter(Loan.user_id == user_id)
    if book_id:
        query = query.filter(Loan.book_id == book_id)
    return query.order_by(Loan.loan_date.desc()).all()

def check_overdue_loans(db: Session) -> int:
    \"\"\"Update status of overdue loans. Returns count of newly overdue loans.\"\"\"
    now = datetime.now(timezone.utc)
    overdue_loans = (
        db.query(Loan)
        .filter(Loan.status == "active", Loan.due_date < now)
        .all()
    )
    for loan in overdue_loans:
        loan.status = "overdue"
    db.commit()
    return len(overdue_loans)
""",
    "app/api/v1/endpoints/books.py": """from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.services import book_service

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    \"\"\"Create a new book in the library catalog.\"\"\"
    return book_service.create_book(db, book)

@router.get("/", response_model=list[BookRead])
def list_books(
    search: str | None = Query(None, description="Search by title or author"),
    genre: str | None = Query(None, description="Filter by genre"),
    available_only: bool = Query(False, description="Show only available books"),
    db: Session = Depends(get_db),
):
    \"\"\"List all books with optional filters.\"\"\"
    return book_service.get_books(db, search=search, genre=genre, available_only=available_only)

@router.get("/{book_id}", response_model=BookRead)
def get_book(book_id: int, db: Session = Depends(get_db)):
    \"\"\"Get a specific book by ID.\"\"\"
    return book_service.get_book(db, book_id)

@router.put("/{book_id}", response_model=BookRead)
def update_book(book_id: int, book: BookUpdate, db: Session = Depends(get_db)):
    \"\"\"Update a book's information.\"\"\"
    return book_service.update_book(db, book_id, book)

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    \"\"\"Delete a book from the catalog.\"\"\"
    book_service.delete_book(db, book_id)
""",
    "app/api/v1/endpoints/users.py": """from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    \"\"\"Register a new library user.\"\"\"
    return user_service.create_user(db, user)

@router.get("/", response_model=list[UserRead])
def list_users(
    search: str | None = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
):
    \"\"\"List all registered users.\"\"\"
    return user_service.get_users(db, search=search)

@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    \"\"\"Get a specific user by ID.\"\"\"
    return user_service.get_user(db, user_id)

@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    \"\"\"Update a user's information.\"\"\"
    return user_service.update_user(db, user_id, user)

@router.put("/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    \"\"\"Deactivate a user account.\"\"\"
    return user_service.deactivate_user(db, user_id)
""",
    "app/api/v1/endpoints/loans.py": """from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.loan import Loan
from app.schemas.loan import LoanCreate, LoanRead
from app.services import loan_service

router = APIRouter(prefix="/loans", tags=["loans"])

def _loan_to_read(loan: Loan) -> LoanRead:
    \"\"\"Convert Loan model to LoanRead schema with expanded names.\"\"\"
    return LoanRead(
        id=loan.id,
        user_id=loan.user_id,
        book_id=loan.book_id,
        loan_date=loan.loan_date,
        due_date=loan.due_date,
        return_date=loan.return_date,
        status=loan.status,
        user_name=loan.user.name if loan.user else None,
        book_title=loan.book.title if loan.book else None,
    )

@router.post("/", response_model=LoanRead, status_code=status.HTTP_201_CREATED)
def create_loan(loan: LoanCreate, db: Session = Depends(get_db)):
    \"\"\"Borrow a book from the library.\"\"\"
    result = loan_service.borrow_book(db, loan.user_id, loan.book_id)
    return _loan_to_read(result)

@router.get("/", response_model=list[LoanRead])
def list_loans(
    status: str | None = Query(None, description="Filter by status: active, returned, overdue"),
    user_id: int | None = Query(None, description="Filter by user ID"),
    book_id: int | None = Query(None, description="Filter by book ID"),
    db: Session = Depends(get_db),
):
    \"\"\"List all loans with optional filters.\"\"\"
    loans = loan_service.get_loans(db, status_filter=status, user_id=user_id, book_id=book_id)
    return [_loan_to_read(loan) for loan in loans]

@router.put("/{loan_id}/return", response_model=LoanRead)
def return_book(loan_id: int, db: Session = Depends(get_db)):
    \"\"\"Return a borrowed book.\"\"\"
    result = loan_service.return_book(db, loan_id)
    return _loan_to_read(result)

@router.post("/check-overdue")
def check_overdue(db: Session = Depends(get_db)):
    \"\"\"Check and update overdue loans.\"\"\"
    count = loan_service.check_overdue_loans(db)
    return {"overdue_count": count}
""",
    "app/api/v1/endpoints/stats.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.book import Book
from app.models.loan import Loan
from app.models.user import User
from app.schemas.stats import DashboardStats
from sqlalchemy import func

router = APIRouter(prefix="/stats", tags=["statistics"])

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    \"\"\"Get dashboard statistics.\"\"\"
    total_books = db.query(func.count(Book.id)).scalar() or 0
    total_users = db.query(func.count(User.id)).scalar() or 0
    active_loans = (
        db.query(func.count(Loan.id)).filter(Loan.status == "active").scalar() or 0
    )
    overdue_loans = (
        db.query(func.count(Loan.id)).filter(Loan.status == "overdue").scalar() or 0
    )
    available_books = (
        db.query(func.count(Book.id)).filter(Book.available_copies > 0).scalar() or 0
    )
    total_copies = db.query(func.sum(Book.quantity)).scalar() or 0

    return DashboardStats(
        total_books=total_books,
        total_users=total_users,
        active_loans=active_loans,
        overdue_loans=overdue_loans,
        available_books=available_books,
        total_copies=total_copies,
    )
""",
    "app/api/v1/router.py": """from fastapi import APIRouter

from app.api.v1.endpoints import books, loans, stats, users

api_router = APIRouter()
api_router.include_router(books.router)
api_router.include_router(users.router)
api_router.include_router(loans.router)
api_router.include_router(stats.router)
""",
    "app/main.py": """from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.database import Base, engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"Create database tables on startup.\"\"\"
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description="Sistema de Gestión de Biblioteca",
    version="1.0.0",
    lifespan=lifespan,
)

# API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Serve static frontend files (must be AFTER API routes)
import os
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
""",
    "app/db/seed.py": """\"\"\"Seed the database with sample data for development/demo.\"\"\"
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.db.database import SessionLocal, engine, Base
from app.models.book import Book
from app.models.user import User
from app.models.loan import Loan

def seed_database():
    \"\"\"Populate the database with sample books, users, and loans.\"\"\"
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    # Check if data already exists
    if db.query(Book).count() > 0:
        print("Database already seeded. Skipping.")
        db.close()
        return

    # Sample books
    books = [
        Book(title="Clean Code", author="Robert C. Martin", isbn="9780132350884",
             genre="Software", published_year=2008, quantity=3, available_copies=2,
             description="A handbook of agile software craftsmanship."),
        Book(title="Design Patterns", author="Gang of Four", isbn="9780201633610",
             genre="Software", published_year=1994, quantity=2, available_copies=1,
             description="Elements of reusable object-oriented software."),
        Book(title="The Pragmatic Programmer", author="David Thomas & Andrew Hunt", isbn="9780135957059",
             genre="Software", published_year=2019, quantity=2, available_copies=2,
             description="Your journey to mastery."),
        Book(title="Cien años de soledad", author="Gabriel García Márquez", isbn="9780060883287",
             genre="Ficción", published_year=1967, quantity=4, available_copies=3,
             description="La saga de la familia Buendía en Macondo."),
        Book(title="El Aleph", author="Jorge Luis Borges", isbn="9780142437889",
             genre="Ficción", published_year=1949, quantity=2, available_copies=2,
             description="Colección de cuentos de Borges."),
        Book(title="Introduction to Algorithms", author="Thomas H. Cormen", isbn="9780262033848",
             genre="Ciencias", published_year=2009, quantity=3, available_copies=3,
             description="The comprehensive textbook on algorithms."),
        Book(title="Rayuela", author="Julio Cortázar", isbn="9788437604572",
             genre="Ficción", published_year=1963, quantity=2, available_copies=1,
             description="Una novela experimental."),
        Book(title="Python Crash Course", author="Eric Matthes", isbn="9781593279288",
             genre="Software", published_year=2019, quantity=5, available_copies=4,
             description="A hands-on, project-based introduction to programming."),
        Book(title="Don Quijote de la Mancha", author="Miguel de Cervantes", isbn="9788420412146",
             genre="Clásicos", published_year=1605, quantity=3, available_copies=3,
             description="La obra cumbre de la literatura en español."),
        Book(title="Refactoring", author="Martin Fowler", isbn="9780134757599",
             genre="Software", published_year=2018, quantity=2, available_copies=2,
             description="Improving the design of existing code."),
    ]
    db.add_all(books)
    db.flush()

    # Sample users
    users = [
        User(name="María González", email="maria.gonzalez@email.com"),
        User(name="Juan Pérez", email="juan.perez@email.com"),
        User(name="Ana López", email="ana.lopez@email.com"),
        User(name="Carlos Rodríguez", email="carlos.rodriguez@email.com"),
        User(name="Laura Martínez", email="laura.martinez@email.com"),
    ]
    db.add_all(users)
    db.flush()

    # Sample active loans
    now = datetime.now(timezone.utc)
    loans = [
        Loan(user_id=users[0].id, book_id=books[0].id,
             loan_date=now - timedelta(days=5), due_date=now + timedelta(days=9)),
        Loan(user_id=users[1].id, book_id=books[1].id,
             loan_date=now - timedelta(days=10), due_date=now + timedelta(days=4)),
        Loan(user_id=users[2].id, book_id=books[6].id,
             loan_date=now - timedelta(days=3), due_date=now + timedelta(days=11)),
        Loan(user_id=users[3].id, book_id=books[3].id,
             loan_date=now - timedelta(days=7), due_date=now + timedelta(days=7)),
        # One returned loan
        Loan(user_id=users[0].id, book_id=books[4].id,
             loan_date=now - timedelta(days=20), due_date=now - timedelta(days=6),
             return_date=now - timedelta(days=8), status="returned"),
    ]
    db.add_all(loans)
    db.commit()
    db.close()
    print(f"Database seeded with {len(books)} books, {len(users)} users, and {len(loans)} loans.")

if __name__ == "__main__":
    seed_database()
"""
}

for rel_path, content in FILES.items():
    full_path = os.path.join(BASE_DIR, rel_path.replace("/", "\\"))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Generated backend files!")
