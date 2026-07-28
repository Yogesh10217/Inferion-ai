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
from app.api.admin import router as admin_router
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager that handles startup initialization and graceful shutdown."""
    if hasattr(app.state, "container"):
        container = app.state.container
        initializer = InfrastructureInitializer(container)
        await initializer.initialize()
    yield
    if hasattr(app.state, "container"):
        app.state.container.logger.info("Shutting down the application and releasing resources...")
        await app.state.container.request_scheduler.shutdown()


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
        
    if settings.prometheus_enabled:
        app.include_router(metrics_router)

    @app.get("/", include_in_schema=False)
    async def root() -> dict[str, str]:
        return {"service": settings.app_name, "status": "ok"}

    return app


app = create_app()

