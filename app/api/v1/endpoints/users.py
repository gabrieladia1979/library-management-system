from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new library user."""
    return user_service.create_user(db, user)


@router.get("/", response_model=list[UserRead])
def list_users(
    search: str | None = Query(None, description="Search by name or email"),
    db: Session = Depends(get_db),
):
    """List all registered users."""
    return user_service.get_users(db, search=search)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get a specific user by ID."""
    return user_service.get_user(db, user_id)


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update a user's information."""
    return user_service.update_user(db, user_id, user)


@router.put("/{user_id}/deactivate", response_model=UserRead)
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """Deactivate a user account."""
    return user_service.deactivate_user(db, user_id)
