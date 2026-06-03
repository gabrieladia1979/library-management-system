import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
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
os.makedirs("static", exist_ok=True)
app.mount("/", StaticFiles(directory="static", html=True), name="static")
