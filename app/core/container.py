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
from app.observability.prometheus_registry import PrometheusRegistry
from app.observability.metrics_mapper import MetricsMapper
from app.observability.prometheus_exporter import PrometheusExporter
from app.core.database import async_session_maker

from app.limits.memory_backend import MemoryCounterBackend
from app.limits.redis_backend import RedisCounterBackend
from app.limits.rate_limit_service import RateLimitService
from app.limits.quota_service import QuotaService
from app.limits.usage_service import UsageService

from app.billing.pricing_service import PricingService
from app.billing.plan_service import PlanService, SubscriptionService
from app.billing.budget_service import BudgetService
from app.billing.invoice_service import InvoiceService
from app.admin import (
    OrganizationAdminService, WorkspaceAdminService, UserAdminService,
    APIKeyAdminService, SubscriptionAdminService, AuditAdminService,
    ReportAdminService, HealthAdminService, SystemAdminService
)


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

        # Initialize limits services
        if self.settings.rate_limit_backend.lower() == "redis":
            self.counter_backend = RedisCounterBackend(redis_url=self.settings.redis_url, metrics=self.metrics_service)
        else:
            self.counter_backend = MemoryCounterBackend()

        self.rate_limit_service = RateLimitService(
            backend=self.counter_backend,
            metrics=self.metrics_service,
            default_strategy=self.settings.default_rate_limit_strategy
        )
        self.quota_service = QuotaService(session_factory=async_session_maker, metrics=self.metrics_service)
        self.usage_service = UsageService(session_factory=async_session_maker, metrics=self.metrics_service)

        # Initialize billing & subscription services
        self.pricing_service = PricingService(session_factory=async_session_maker)
        self.plan_service = PlanService(session_factory=async_session_maker)
        self.subscription_service = SubscriptionService(session_factory=async_session_maker)
        self.budget_service = BudgetService(session_factory=async_session_maker, metrics_service=self.metrics_service)
        self.invoice_service = InvoiceService(session_factory=async_session_maker, pricing_service=self.pricing_service, metrics=self.metrics_service)
        
        # Admin Services
        self.organization_admin_service = OrganizationAdminService(async_session_maker)
        self.workspace_admin_service = WorkspaceAdminService(async_session_maker)
        self.user_admin_service = UserAdminService(async_session_maker)
        self.api_key_admin_service = APIKeyAdminService(async_session_maker)
        self.subscription_admin_service = SubscriptionAdminService(async_session_maker)
        self.audit_admin_service = AuditAdminService(async_session_maker)
        self.report_admin_service = ReportAdminService(async_session_maker)
        self.health_admin_service = HealthAdminService(async_session_maker)
        self.system_admin_service = SystemAdminService(async_session_maker)

        # Initialize default inference service
        self.inference_service = DefaultInferenceService(
            registry=self.registry,
            provider=None,
            request_router=self.request_router,
            streaming_manager=self.streaming_manager,
            request_scheduler=self.request_scheduler,
            usage_emitter=self.usage_service,
        )

        # Initialize health service
        self.health_service = HealthService(
            provider_factory=self.provider_factory,
            registry=self.registry,
            metrics_service=self.metrics_service,
            startup_time=self.startup_time,
            app_version=self.settings.app_version,
        )

        # Observability Platform Manager (Phase 5.8)
        from app.observability.manager import ObservabilityManager
        self.observability_manager = ObservabilityManager(
            pricing_service=self.pricing_service,
            session_factory=async_session_maker,
        )

        # Observability / Prometheus
        if self.settings.prometheus_enabled:
            self.prometheus_registry = PrometheusRegistry(
                namespace=self.settings.prometheus_namespace,
                subsystem=self.settings.prometheus_subsystem,
            )
            self.metrics_mapper = MetricsMapper(
                registry=self.prometheus_registry,
                metrics_service=self.metrics_service,
                version=self.settings.app_version,
            )
            self.prometheus_exporter = PrometheusExporter(self.metrics_mapper)
        else:
            self.prometheus_registry = None
            self.metrics_mapper = None
            self.prometheus_exporter = None

        # Phase 5.9 — Reliability, Security & Infrastructure Platform
        from app.security import (
            AuthenticationManager, AuthorizationEngine, APIKeyManager, SecretManager
        )
        from app.governance import (
            RateLimiter, QuotaManager, ResourceGovernanceEngine
        )
        from app.resilience import (
            CircuitBreakerRegistry, RetryManager, BulkheadRegistry, TimeoutManager, FallbackManager
        )
        from app.jobs import JobQueue, WorkerPool, JobScheduler
        from app.persistence import DatabaseHealthMonitor, TransactionManager, BackupManager, RestoreManager
        from app.cache.distributed_lock import DistributedLockManager
        from app.reliability import SystemHealthManager, GracefulShutdownManager
        from app.config import ConfigurationValidator

        self.authentication_manager = AuthenticationManager(secret_key=self.settings.jwt_secret)
        self.authorization_engine = AuthorizationEngine()
        self.api_key_manager = APIKeyManager()
        self.secret_manager = SecretManager()

        self.rate_limiter = RateLimiter()
        self.quota_manager = QuotaManager()
        self.resource_governance = ResourceGovernanceEngine(
            rate_limiter=self.rate_limiter,
            quota_manager=self.quota_manager,
        )

        self.circuit_breaker_registry = CircuitBreakerRegistry()
        self.retry_manager = RetryManager()
        self.bulkhead_registry = BulkheadRegistry()
        self.timeout_manager = TimeoutManager()
        self.fallback_manager = FallbackManager()

        self.job_queue = JobQueue()
        self.worker_pool = WorkerPool(queue=self.job_queue)
        self.job_scheduler = JobScheduler(queue=self.job_queue)

        self.database_health_monitor = DatabaseHealthMonitor(session_factory=async_session_maker)
        self.transaction_manager = TransactionManager(session_factory=async_session_maker)
        self.backup_manager = BackupManager()
        self.restore_manager = RestoreManager(backup_manager=self.backup_manager)

        self.distributed_lock_manager = DistributedLockManager()
        self.system_health_manager = SystemHealthManager()
        self.system_health_manager.register_dependency_checker("database", self.database_health_monitor)
        self.graceful_shutdown_manager = GracefulShutdownManager()
        self.configuration_validator = ConfigurationValidator()

        # Phase 5.10 — Enterprise Control Plane
        from app.control_plane import ControlPlaneManager
        self.control_plane_manager = ControlPlaneManager()

        # Phase 5.11 — Developer Platform & Marketplace
        from app.developer_platform.manager import DeveloperPlatformManager
        from app.extensions.manager import ExtensionManager
        from app.marketplace.manager import MarketplaceManager

        self.developer_platform_manager = DeveloperPlatformManager()
        self.extension_manager = ExtensionManager()
        self.marketplace_manager = MarketplaceManager()





