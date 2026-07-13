from __future__ import annotations

import logging
from app.core.container import ServiceContainer
from app.registry.model_metadata import ModelMetadata

logger = logging.getLogger("app")


class InfrastructureInitializer:
    """Initializer responsible for preparing the application infrastructure during startup."""

    def __init__(self, container: ServiceContainer) -> None:
        self._container = container

    async def initialize(self) -> None:
        """Run all startup initialization tasks."""
        logger.info("Initializing providers...")
        factory = self._container.provider_factory

        # Perform provider health checks
        logger.info("Performing provider health checks...")
        provider_statuses = {}
        for name in factory.list_providers():
            try:
                provider = factory.get_provider(name)
                is_healthy = await provider.health_check()
                provider_statuses[name] = "healthy" if is_healthy else "unhealthy"
            except Exception as e:
                provider_statuses[name] = f"error: {str(e)}"
                logger.error(f"Provider '{name}' health check failed: {e}")

        # Discover models and populate registry
        logger.info("Discovering available models...")
        registry = self._container.registry
        discovered_count = 0
        for name in factory.list_providers():
            try:
                provider = factory.get_provider(name)
                provider_models = await provider.list_models()
                for pm in provider_models:
                    # Register/update the discovered model in the registry
                    model_meta = ModelMetadata(
                        id=pm.id,
                        provider=pm.provider,
                        description=pm.description,
                        context_window=pm.context_window,
                        status=pm.status,
                    )
                    registry.register_model(model_meta)
                    discovered_count += 1
            except Exception as e:
                logger.error(f"Failed to discover models for provider '{name}': {e}")

        # Print startup summary
        self._print_summary(provider_statuses, discovered_count)

    def _print_summary(self, provider_statuses: dict[str, str], discovered_count: int) -> None:
        """Log a formatted startup summary."""
        registry = self._container.registry

        logger.info("=" * 50)
        logger.info("⚡ LLM INFERENCE ENGINE STARTUP SUMMARY ⚡")
        logger.info(f"App Name:    {self._container.settings.app_name}")
        logger.info(f"Environment: {self._container.settings.environment}")
        logger.info(f"Log Level:   {self._container.settings.log_level}")
        logger.info("-" * 50)
        logger.info("Providers:")
        for name, status in provider_statuses.items():
            logger.info(f"  - {name:<10} [{status}]")
        logger.info("-" * 50)
        logger.info(f"Model Registry (Total: {len(registry.list_models())}, Discovered: {discovered_count}):")
        for model in registry.list_models():
            logger.info(f"  - {model.id:<15} | Provider: {model.provider:<10} | Status: {model.status}")
        logger.info("=" * 50)
