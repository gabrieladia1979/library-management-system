from fastapi import APIRouter

from app.api.v1.endpoints import books, loans, stats, users

api_router = APIRouter()
api_router.include_router(books.router)
api_router.include_router(users.router)
api_router.include_router(loans.router)
api_router.include_router(stats.router)
