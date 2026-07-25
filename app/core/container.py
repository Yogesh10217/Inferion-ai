from __future__ import annotations

from datetime import datetime, timezone

from app.core.config import Settings, get_settings
from app.core.logger import get_logger, setup_logging
from app.providers.provider_factory import ProviderFactory
from app.registry.model_registry import InMemoryModelRegistry
from app.routing.model_strategy import ModelBasedRoutingStrategy
from app.routing.request_router import RequestRouter
from app.services.inference_service import DefaultInferenceService
from app.services.metrics_service import MetricsService
from app.services.health_service import HealthService
from app.services.streaming_manager import StreamingManager
from app.services.request_scheduler import RequestScheduler


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

        # Initialize startup time
        self.startup_time = datetime.now(timezone.utc)

        # Initialize provider factory
        self.provider_factory = ProviderFactory()

        # Initialize model registry
        self.registry = InMemoryModelRegistry()

        # Initialize request router with model-based routing strategy
        self.request_router = RequestRouter(
            registry=self.registry,
            strategy=ModelBasedRoutingStrategy(),
        )

        # Initialize metrics service (needed by scheduler, health, batching, load balancing)
        self.metrics_service = MetricsService()

        # Initialize Provider Pool and Load Balancer
        from app.routing.provider_pool import ProviderPool, ProviderInstance
        from app.routing.load_balancer import LoadBalancer
        from app.routing.load_balancing_policy import get_policy, LoadBalancingStrategy
        from app.routing.failover_policy import FailoverPolicy

        self.provider_pool = ProviderPool()
        
        # Populate ProviderPool with backward-compatible defaults from ProviderFactory
        for provider_name in self.provider_factory.list_providers():
            try:
                base_provider = self.provider_factory.get_provider(provider_name)
                # Create a default instance for the provider
                instance = ProviderInstance(
                    provider_id=provider_name,
                    instance_id=f"{provider_name}-default",
                    provider=base_provider,
                    base_url=getattr(base_provider, 'base_url', None)
                )
                self.provider_pool.register_instance(instance)
            except Exception as exc:
                self.logger.warning(f"Failed to auto-register instance for {provider_name}: {exc}")

        policy_enum = LoadBalancingStrategy(self.settings.load_balancing_policy)
        self.load_balancing_policy = get_policy(policy_enum)
        self.load_balancer = LoadBalancer(pool=self.provider_pool, policy=self.load_balancing_policy)
        
        self.failover_policy = FailoverPolicy(load_balancer=self.load_balancer)

        # Initialize Cache
        from app.cache.cache_manager import CacheManager
        from app.cache.cache_policy import CachePolicy
        from app.cache.memory_backend import MemoryCacheBackend
        from app.cache.redis_backend import RedisCacheBackend

        if self.settings.cache_backend.lower() == "redis":
            cache_backend = RedisCacheBackend(redis_url=self.settings.redis_url)
        else:
            cache_backend = MemoryCacheBackend()

        self.cache_policy = CachePolicy(
            ttl_seconds=self.settings.cache_ttl_seconds,
            no_cache=not self.settings.cache_enabled
        )

        self.cache_manager = CacheManager(
            backend=cache_backend,
            policy=self.cache_policy,
            metrics=self.metrics_service,
            enabled=self.settings.cache_enabled
        )

        # Initialize batching
        from app.services.batching.batch_config import BatchConfig
        from app.services.batching.batch_policy import BatchPolicy
        from app.services.batching.batch_executor import BatchExecutor
        from app.services.batching.batch_collector import BatchCollector

        self.batch_config = BatchConfig(
            enabled=self.settings.batch_enabled,
            max_batch_size=self.settings.batch_max_size,
            max_batch_wait_ms=self.settings.batch_max_wait_ms,
            max_queue_tokens=self.settings.batch_max_queue_tokens,
        )
        self.batch_policy = BatchPolicy(config=self.batch_config)
        self.batch_executor = BatchExecutor(
            failover_policy=self.failover_policy, 
            metrics=self.metrics_service,
            cache_manager=self.cache_manager
        )
        self.batch_collector = BatchCollector(
            policy=self.batch_policy,
            executor=self.batch_executor,
            metrics=self.metrics_service,
        )

        # Initialize request scheduler
        self.request_scheduler = RequestScheduler(
            router=self.request_router,
            metrics=self.metrics_service,
            batch_collector=self.batch_collector,
        )

        # Initialize streaming manager
        self.streaming_manager = StreamingManager(scheduler=self.request_scheduler)

        # Initialize default inference service
        self.inference_service = DefaultInferenceService(
            registry=self.registry,
            provider=None,
            request_router=self.request_router,
            streaming_manager=self.streaming_manager,
            request_scheduler=self.request_scheduler,
        )

        # Initialize health service
        self.health_service = HealthService(
            provider_factory=self.provider_factory,
            registry=self.registry,
            metrics_service=self.metrics_service,
            startup_time=self.startup_time,
            app_version=self.settings.app_version,
        )

