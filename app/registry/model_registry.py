from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from threading import RLock
from typing import Literal


ModelStatus = Literal["available", "loading", "degraded", "unavailable"]


@dataclass(slots=True)
class RegisteredModel:
    """Represents a single model entry in the registry."""

    id: str
    provider: str
    description: str = ""
    context_window: int | None = None
    status: ModelStatus = "available"


class ModelRegistry(ABC):
    """Repository interface for managing model metadata."""

    @abstractmethod
    def register_model(self, model: RegisteredModel) -> RegisteredModel:
        """Persist a model entry and return the stored instance."""
        raise NotImplementedError

    @abstractmethod
    def unregister_model(self, model_id: str) -> None:
        """Remove a model from the registry if it exists."""
        raise NotImplementedError

    @abstractmethod
    def get_model(self, model_id: str) -> RegisteredModel | None:
        """Return a model by identifier or None if it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> list[RegisteredModel]:
        """Return all known models."""
        raise NotImplementedError

    @abstractmethod
    def model_exists(self, model_id: str) -> bool:
        """Return whether a model is present in the registry."""
        raise NotImplementedError


class InMemoryModelRegistry(ModelRegistry):
    """Thread-safe in-memory registry implementation.

    This implementation is intentionally backend-agnostic so it can later be
    replaced by Redis, PostgreSQL, or another persistence store without changing
    the public interface used by the application.
    """

    def __init__(self) -> None:
        self._models: dict[str, RegisteredModel] = {}
        self._lock = RLock()
        self._seed()

    def _seed(self) -> None:
        with self._lock:
            self._models["gpt-4o-mini"] = RegisteredModel(
                id="gpt-4o-mini",
                provider="openai",
                description="OpenAI GPT-4o mini",
                context_window=128000,
                status="available",
            )
            self._models["llama3.1"] = RegisteredModel(
                id="llama3.1",
                provider="ollama",
                description="Ollama local Llama 3.1",
                context_window=8192,
                status="available",
            )

    def register_model(self, model: RegisteredModel) -> RegisteredModel:
        with self._lock:
            self._models[model.id] = model
            return model

    def unregister_model(self, model_id: str) -> None:
        with self._lock:
            self._models.pop(model_id, None)

    def get_model(self, model_id: str) -> RegisteredModel | None:
        with self._lock:
            return self._models.get(model_id)

    def list_models(self) -> list[RegisteredModel]:
        with self._lock:
            return list(self._models.values())

    def model_exists(self, model_id: str) -> bool:
        with self._lock:
            return model_id in self._models
