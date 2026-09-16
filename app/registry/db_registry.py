from __future__ import annotations

import logging
from datetime import datetime, timezone
from threading import RLock
from typing import Any

from sqlalchemy import select

from app.core.database import async_session_maker
from app.registry.model_metadata import ModelMetadata
from app.registry.models import ModelRegistration
from app.registry.repository import ModelRegistry

logger = logging.getLogger("app.registry.db_registry")


class DatabaseModelRegistry(ModelRegistry):
    """Database-backed Model Registry with write-through in-memory caching."""

    def __init__(self, session_factory=None) -> None:
        self._session_factory = session_factory or async_session_maker
        self._cache: dict[str, ModelMetadata] = {}
        self._lock = RLock()
        self._seed_default_cache()

    def _seed_default_cache(self) -> None:
        with self._lock:
            self._cache["gpt-4o-mini"] = ModelMetadata(
                id="gpt-4o-mini",
                provider="openai",
                description="OpenAI GPT-4o mini",
                context_window=128000,
                status="available",
            )
            self._cache["llama3.1"] = ModelMetadata(
                id="llama3.1",
                provider="ollama",
                description="Ollama local Llama 3.1",
                context_window=8192,
                status="available",
            )

    async def load_from_db(self) -> None:
        """Load all model registrations from the database into local cache."""
        async with self._session_factory() as session:
            stmt = select(ModelRegistration)
            result = await session.execute(stmt)
            records = result.scalars().all()
            if records:
                with self._lock:
                    for rec in records:
                        self._cache[rec.id] = ModelMetadata(
                            id=rec.id,
                            provider=rec.provider,
                            description=rec.description or "",
                            context_window=rec.context_window or 128000,
                            status=rec.status or "available",
                            created_at=rec.created_at,
                            updated_at=rec.updated_at,
                        )
            else:
                # Seed defaults into database
                for model in list(self._cache.values()):
                    db_rec = ModelRegistration(
                        id=model.id,
                        provider=model.provider,
                        description=model.description,
                        context_window=model.context_window,
                        status=model.status,
                    )
                    session.add(db_rec)
                try:
                    await session.commit()
                except Exception as exc:
                    await session.rollback()
                    logger.warning(f"Failed to seed models into DB: {exc}")

    def register_model(self, model: ModelMetadata) -> ModelMetadata:
        with self._lock:
            self._cache[model.id] = model

        # Asynchronously or synchronously write to DB in background
        async def _persist():
            async with self._session_factory() as session:
                stmt = select(ModelRegistration).where(ModelRegistration.id == model.id)
                res = await session.execute(stmt)
                existing = res.scalar_one_or_none()
                if existing:
                    existing.provider = model.provider
                    existing.description = model.description
                    existing.context_window = model.context_window
                    existing.status = model.status
                    existing.updated_at = datetime.now(timezone.utc)
                else:
                    db_rec = ModelRegistration(
                        id=model.id,
                        provider=model.provider,
                        description=model.description,
                        context_window=model.context_window,
                        status=model.status,
                    )
                    session.add(db_rec)
                await session.commit()

        try:
            import asyncio
            loop = asyncio.get_running_loop()
            loop.create_task(_persist())
        except RuntimeError:
            pass

        return model

    def update_model(self, model_id: str, updates: dict[str, Any]) -> ModelMetadata:
        with self._lock:
            model = self._cache.get(model_id)
            if model is None:
                raise KeyError(f"Model '{model_id}' was not found")
            for k, v in updates.items():
                if hasattr(model, k):
                    setattr(model, k, v)
            model.updated_at = datetime.now(timezone.utc)

        async def _persist_update():
            async with self._session_factory() as session:
                stmt = select(ModelRegistration).where(ModelRegistration.id == model_id)
                res = await session.execute(stmt)
                rec = res.scalar_one_or_none()
                if rec:
                    for k, v in updates.items():
                        if hasattr(rec, k):
                            setattr(rec, k, v)
                    rec.updated_at = datetime.now(timezone.utc)
                    await session.commit()

        try:
            import asyncio
            loop = asyncio.get_running_loop()
            loop.create_task(_persist_update())
        except RuntimeError:
            pass

        return model

    def remove_model(self, model_id: str) -> None:
        with self._lock:
            self._cache.pop(model_id, None)

        async def _persist_delete():
            async with self._session_factory() as session:
                stmt = select(ModelRegistration).where(ModelRegistration.id == model_id)
                res = await session.execute(stmt)
                rec = res.scalar_one_or_none()
                if rec:
                    await session.delete(rec)
                    await session.commit()

        try:
            import asyncio
            loop = asyncio.get_running_loop()
            loop.create_task(_persist_delete())
        except RuntimeError:
            pass

    def unregister_model(self, model_id: str) -> None:
        self.remove_model(model_id)

    def get_model(self, model_id: str) -> ModelMetadata | None:
        with self._lock:
            return self._cache.get(model_id)

    def list_models(self) -> list[ModelMetadata]:
        with self._lock:
            return list(self._cache.values())

    def model_exists(self, model_id: str) -> bool:
        with self._lock:
            return model_id in self._cache

    def list_by_provider(self, provider: str) -> list[ModelMetadata]:
        with self._lock:
            return [m for m in self._cache.values() if m.provider == provider]

    def list_available_models(self) -> list[ModelMetadata]:
        with self._lock:
            return [m for m in self._cache.values() if m.status == "available"]
