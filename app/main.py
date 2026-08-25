from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.models import router as models_router
from app.api.metrics import router as metrics_router
from app.core.config import get_settings
from app.core.container import ServiceContainer
from app.core.initializer import InfrastructureInitializer
from app.core.exceptions import register_exception_handlers
from app.core.middleware import ObservationMiddleware
from app.auth.middleware import AuthenticationMiddleware, AuthorizationMiddleware
from app.tenant.middleware import TenantMiddleware
from app.api.auth import router as auth_router
from app.api.admin_router import admin_router
from app.api.organizations import router as org_router
from app.api.workspaces import router as ws_router
from app.api.quotas import router as quotas_router
from app.api.usage import router as usage_router
from app.limits.middleware import RateLimitMiddleware
from app.billing.middleware import BudgetMiddleware
from app.api.plans import router as plans_router
from app.api.subscriptions import router as subscriptions_router
from app.api.budgets import router as budgets_router
from app.api.billing import router as billing_router
from app.api.webhooks import router as webhooks_router
from app.api.v1.agents import router as agents_router
from app.api.v1.workflows import router as workflows_router
from app.api.v1.memory import router as memory_router
from app.api.v1.tools import router as tools_router
from app.api.v1.teams import router as teams_router
from app.api.v1.planning import router as planning_router
from app.api.v1.autonomy import router as autonomy_router
from app.api.v1.workers import router as workers_router
from app.api.v1.observability import router as observability_router
from app.api.v1.security import router as security_router
from app.api.v1.governance import router as governance_router
from app.api.v1.jobs import router as jobs_router
from app.api.v1.reliability import router as reliability_router
from app.api.v1.control_plane import router as control_plane_router
from app.api.v1.developers import router as developers_router
from app.api.v1.extensions import router as extensions_router
from app.api.v1.marketplace import router as marketplace_router
from app.api.v1.data_fabric import router as data_fabric_router
from app.api.v1.mlops import router as mlops_router
from app.api.v1.finops import router as finops_router
from app.api.v1.operations import router as operations_router
from app.api.v1.governance_platform import router as governance_platform_router
from app.api.v1.identity import router as identity_router
from app.api.v1.orchestration import router as orchestration_router
from app.api.v1.knowledge_platform import router as knowledge_platform_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.developer_platform import router as developer_platform_router
from app.api.v1.application_platform import router as application_platform_router
from app.api.v1.platform_operations import router as platform_operations_router
from app.api.v1.intelligence import router as intelligence_router
from app.api.v1.data_governance import router as data_governance_router
from app.api.v1.architecture import router as architecture_router
from app.api.v1.compliance import router as compliance_router
from app.api.v1.portfolio import router as portfolio_router
from app.api.v1.decisions import router as decisions_router
from app.api.v1.security_intelligence import router as security_intelligence_router
from app.api.v1.ai_lifecycle import router as ai_lifecycle_router























from app.events import InMemoryEventBus, EventPublisher, EventDispatcher, EventRegistry
from app.core.database import async_session_maker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that handles startup initialization and graceful shutdown."""
    if hasattr(app.state, "container"):
        container = app.state.container
        initializer = InfrastructureInitializer(container)
        await initializer.initialize()

        # Initialize Event Platform components
        if not hasattr(container, "event_bus"):
            container.event_bus = InMemoryEventBus()
            container.event_publisher = EventPublisher(container.event_bus, container.metrics_service)
            container.event_dispatcher = EventDispatcher(
                event_bus=container.event_bus,
                session_factory=async_session_maker,
                metrics_service=container.metrics_service,
            )
            container.event_dispatcher.start()

        # Emit system.startup event
        await container.event_publisher.publish(
            EventRegistry.SYSTEM_STARTUP,
            payload={"app_name": container.settings.app_name, "version": container.settings.app_version},
        )

        # Initialize plugins
        from app.plugins import PluginManager
        container.plugin_manager = PluginManager()
        await container.plugin_manager.initialize()

    yield

    if hasattr(app.state, "container"):
        container = app.state.container
        container.logger.info("Shutting down the application and releasing resources...")
        
        # Emit system.shutdown event
        if hasattr(container, "event_publisher"):
            await container.event_publisher.publish(
                EventRegistry.SYSTEM_SHUTDOWN,
                payload={"app_name": container.settings.app_name},
            )
        if hasattr(container, "event_dispatcher"):
            container.event_dispatcher.stop()

        await container.request_scheduler.shutdown()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    # Create service container to manage application state
    container = ServiceContainer(settings)

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    app.state.container = container

    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    
    # Auth Middlewares
    app.add_middleware(BudgetMiddleware, budget_service=container.budget_service)
    app.add_middleware(RateLimitMiddleware, rate_limit_service=container.rate_limit_service, quota_service=container.quota_service)
    app.add_middleware(AuthorizationMiddleware)
    app.add_middleware(TenantMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    
    # Observability
    app.add_middleware(ObservationMiddleware)
    
    # Register exception handlers
    register_exception_handlers(app)

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(models_router, prefix=settings.api_prefix)
    app.include_router(chat_router, prefix=settings.api_prefix)
    app.include_router(admin_router, prefix=settings.api_prefix)
    app.include_router(agents_router)
    app.include_router(workflows_router)
    app.include_router(memory_router)
    app.include_router(tools_router)
    app.include_router(teams_router)
    app.include_router(planning_router)
    app.include_router(autonomy_router)
    app.include_router(workers_router)
    app.include_router(observability_router)
    app.include_router(security_router)
    app.include_router(governance_router)
    app.include_router(jobs_router)
    app.include_router(reliability_router)
    app.include_router(control_plane_router)
    app.include_router(developers_router)
    app.include_router(extensions_router)
    app.include_router(marketplace_router)
    app.include_router(data_fabric_router)
    app.include_router(mlops_router)
    app.include_router(finops_router)
    app.include_router(operations_router)
    app.include_router(governance_platform_router)
    app.include_router(identity_router)
    app.include_router(orchestration_router)
    app.include_router(knowledge_platform_router)
    app.include_router(integrations_router)
    app.include_router(developer_platform_router)
    app.include_router(application_platform_router)
    app.include_router(platform_operations_router)
    app.include_router(intelligence_router)
    app.include_router(data_governance_router)
    app.include_router(architecture_router)
    app.include_router(compliance_router)
    app.include_router(portfolio_router)
    app.include_router(decisions_router)
    app.include_router(security_intelligence_router)
    app.include_router(ai_lifecycle_router)
























    
    if settings.auth_enabled:
        app.include_router(auth_router, prefix=settings.api_prefix)
        app.include_router(admin_router, prefix=settings.api_prefix)
        app.include_router(org_router, prefix=settings.api_prefix)
        app.include_router(ws_router, prefix=settings.api_prefix)
        app.include_router(quotas_router, prefix=settings.api_prefix)
        app.include_router(usage_router, prefix=settings.api_prefix)
        
        # Billing
        app.include_router(plans_router, prefix=settings.api_prefix)
        app.include_router(subscriptions_router, prefix=settings.api_prefix)
        app.include_router(budgets_router, prefix=settings.api_prefix)
        app.include_router(billing_router, prefix=settings.api_prefix)
        
        # Webhooks
        app.include_router(webhooks_router, prefix=settings.api_prefix)
        
        # Plugins
        from app.plugins.plugin_api import router as plugins_router
        app.include_router(plugins_router, prefix=settings.api_prefix)
        
    if settings.prometheus_enabled:
        app.include_router(metrics_router)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"service": settings.app_name, "status": "ok"}

    return app


app = create_app()

