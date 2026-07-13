from __future__ import annotations

import logging
from typing import Any

from app.core.config import Settings, get_settings
from app.core.logger import get_logger, setup_logging
from app.providers.provider_factory import ProviderFactory
from app.registry.model_registry import InMemoryModelRegistry, ModelRegistry
from app.routing.model_strategy import ModelBasedRoutingStrategy
from app.routing.request_router import RequestRouter
from app.services.inference_service import DefaultInferenceService, InferenceService


class ServiceContainer:
    """Dependency injection container for LLM Inference Engine services.

    Manages singletons/instances of core services, including settings, logging,
    providers, request routing, registry, and inference services, avoiding
    global state.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

        # Initialize logging
        setup_logging(self.settings.log_level)
        self.logger = get_logger("app")

        # Initialize provider factory
        self.provider_factory = ProviderFactory()

        # Initialize model registry
        self.registry = InMemoryModelRegistry()

        # Initialize request router with model-based routing strategy
        self.request_router = RequestRouter(
            registry=self.registry,
            strategy=ModelBasedRoutingStrategy(),
            provider_factory=self.provider_factory,
        )

        # Initialize default inference service
        self.inference_service = DefaultInferenceService(
            registry=self.registry,
            provider=None,
            request_router=self.request_router,
        )
