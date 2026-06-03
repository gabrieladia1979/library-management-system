from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user. Raises 409 if email already exists."""
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
    """Get all users with optional search filter."""
    query = db.query(User)
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%"))
        )
    return query.order_by(User.name).all()


def get_user(db: Session, user_id: int) -> User:
    """Get a single user by ID. Raises 404 if not found."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found.",
        )
    return user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> User:
    """Update a user partially. Raises 404 if not found."""
    user = get_user(db, user_id)
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    return user


def deactivate_user(db: Session, user_id: int) -> User:
    """Deactivate a user. Raises 409 if user has active loans."""
    user = get_user(db, user_id)
    active_loans = [loan for loan in user.loans if loan.status == "active"]
    if active_loans:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot deactivate user with active loans.",
        )
    user.is_active = False
    db.commit()
    db.refresh(user)
    return user
