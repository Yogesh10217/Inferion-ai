import logging
import os
import ssl
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings

logger = logging.getLogger("app")

settings = get_settings()

db_url = settings.database_url
connect_args = {}

if db_url.startswith("sqlite"):
    db_path = db_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
    dir_name = os.path.dirname(db_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
elif "postgresql+asyncpg" in db_url or "postgres+asyncpg" in db_url:
    # asyncpg dialect does not support `sslmode` as a connection parameter.
    # Strip `sslmode` and `channel_binding` from URL query string and pass SSL context via connect_args.
    if "?" in db_url:
        base_url, query_str = db_url.split("?", 1)
        params = [
            p for p in query_str.split("&")
            if not p.startswith("sslmode=") and not p.startswith("channel_binding=")
        ]
        db_url = base_url + ("?" + "&".join(params) if params else "")

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_ctx

engine = create_async_engine(
    db_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
    connect_args=connect_args,
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
import app.observability.models
import app.registry.models
import app.mlops.models


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
        db_path = settings.database_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", "")
        dir_name = os.path.dirname(db_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created.")
