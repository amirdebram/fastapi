from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.dependencies.__database__ import create_database
from app.dependencies.__redis__ import redis_manager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Context manager for FastAPI app, handles startup and shutdown tasks."""
    try:
        await create_database()
        await redis_manager.init_client()
    except Exception as e:
        raise RuntimeError("Failed to initialize resources on startup") from e
    yield
    try:
        await redis_manager.close_client()
    except Exception as e:
        raise RuntimeError("Failed to clean up resources on shutdown") from e