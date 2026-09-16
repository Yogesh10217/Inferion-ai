from fastapi import APIRouter, Depends, Request

from app.services.health_service import HealthService

router = APIRouter(tags=["health"])


def get_health_service(request: Request) -> HealthService:
    """Dependency injection provider for the health service."""
    if hasattr(request.app.state, "container"):
        return request.app.state.container.health_service
    # Fallback to raising configuration exception or initializing
    raise RuntimeError("ServiceContainer not initialized in application state.")


@router.get("/health", include_in_schema=True)
async def health(service: HealthService = Depends(get_health_service)) -> dict:
    """Return a basic health status for the service."""
    return await service.get_health_status(endpoint="health")


@router.get("/ready", include_in_schema=True)
async def ready(service: HealthService = Depends(get_health_service)) -> dict:
    """Return readiness information for the service."""
    return await service.get_health_status(endpoint="ready")


@router.get("/live", include_in_schema=True)
async def live(service: HealthService = Depends(get_health_service)) -> dict:
    """Return liveness information for the service."""
    return await service.get_health_status(endpoint="live")
