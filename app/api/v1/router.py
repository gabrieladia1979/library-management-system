from fastapi import APIRouter, Depends

from app.api.v1.endpoints import auth, books, loans, stats, users
from app.core.security import get_current_user

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(books.router, dependencies=[Depends(get_current_user)])
api_router.include_router(users.router, dependencies=[Depends(get_current_user)])
api_router.include_router(loans.router, dependencies=[Depends(get_current_user)])
api_router.include_router(stats.router, dependencies=[Depends(get_current_user)])
