import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

logger = logging.getLogger("app")

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()

# Import all models to ensure they are registered with Base
import app.auth.models
import app.tenant.models
import app.limits.models
import app.billing.models
import app.admin.models
import app.events.event_models
import app.knowledge.models


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for injecting the database session.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            raise e


async def init_db() -> None:
    """
    Initializes the database tables. Used for SQLite in development mode,
    or during bootstrap.
    """
    if settings.database_url.startswith("sqlite"):
        # Make sure the data directory exists
        import os
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "")
        if db_path.startswith("./"):
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created.")
