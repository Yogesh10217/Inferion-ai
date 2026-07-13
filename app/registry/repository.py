from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.registry.model_metadata import ModelMetadata


class ModelRegistry(ABC):
    """Repository interface for managing model metadata."""

    @abstractmethod
    def register_model(self, model: ModelMetadata) -> ModelMetadata:
        """Persist a model entry and return the stored instance."""
        raise NotImplementedError

    @abstractmethod
    def update_model(self, model_id: str, updates: dict[str, Any]) -> ModelMetadata:
        """Update fields of an existing model."""
        raise NotImplementedError

    @abstractmethod
    def remove_model(self, model_id: str) -> None:
        """Remove a model from the registry if it exists."""
        raise NotImplementedError

    @abstractmethod
    def get_model(self, model_id: str) -> ModelMetadata | None:
        """Return a model by identifier or None if it does not exist."""
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> list[ModelMetadata]:
        """Return all known models."""
        raise NotImplementedError

    @abstractmethod
    def model_exists(self, model_id: str) -> bool:
        """Return whether a model is present in the registry."""
        raise NotImplementedError

    @abstractmethod
    def list_by_provider(self, provider: str) -> list[ModelMetadata]:
        """Return all models belonging to a specific provider."""
        raise NotImplementedError

    @abstractmethod
    def list_available_models(self) -> list[ModelMetadata]:
        """Return all models that have an 'available' status."""
        raise NotImplementedError

    def unregister_model(self, model_id: str) -> None:
        """Alias for remove_model to maintain backward compatibility."""
        self.remove_model(model_id)
