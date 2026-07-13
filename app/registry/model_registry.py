from __future__ import annotations

from datetime import datetime, timezone
from threading import RLock
from typing import Any

from app.registry.model_metadata import ModelMetadata, ModelStatus, RegisteredModel
from app.registry.repository import ModelRegistry


class InMemoryModelRegistry(ModelRegistry):
    """Thread-safe in-memory registry implementation.

    This implementation is intentionally backend-agnostic so it can later be
    replaced by Redis, PostgreSQL, or another persistence store without changing
    the public interface used by the application.
    """

    def __init__(self) -> None:
        self._models: dict[str, ModelMetadata] = {}
        self._lock = RLock()
        self._seed()

    def _seed(self) -> None:
        with self._lock:
            self._models["gpt-4o-mini"] = ModelMetadata(
                id="gpt-4o-mini",
                provider="openai",
                description="OpenAI GPT-4o mini",
                context_window=128000,
                status="available",
            )
            self._models["llama3.1"] = ModelMetadata(
                id="llama3.1",
                provider="ollama",
                description="Ollama local Llama 3.1",
                context_window=8192,
                status="available",
            )

    def register_model(self, model: ModelMetadata) -> ModelMetadata:
        with self._lock:
            self._models[model.id] = model
            return model

    def update_model(self, model_id: str, updates: dict[str, Any]) -> ModelMetadata:
        with self._lock:
            model = self._models.get(model_id)
            if model is None:
                raise KeyError(f"Model '{model_id}' was not found")
            for k, v in updates.items():
                if hasattr(model, k):
                    setattr(model, k, v)
            model.updated_at = datetime.now(timezone.utc)
            return model

    def remove_model(self, model_id: str) -> None:
        with self._lock:
            self._models.pop(model_id, None)

    def unregister_model(self, model_id: str) -> None:
        self.remove_model(model_id)

    def get_model(self, model_id: str) -> ModelMetadata | None:
        with self._lock:
            return self._models.get(model_id)

    def list_models(self) -> list[ModelMetadata]:
        with self._lock:
            return list(self._models.values())

    def model_exists(self, model_id: str) -> bool:
        with self._lock:
            return model_id in self._models

    def list_by_provider(self, provider: str) -> list[ModelMetadata]:
        with self._lock:
            return [m for m in self._models.values() if m.provider == provider]

    def list_available_models(self) -> list[ModelMetadata]:
        with self._lock:
            return [m for m in self._models.values() if m.status == "available"]
