from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health", include_in_schema=True)
async def health() -> dict[str, str]:
    """Return a basic health status for the service."""
    return {"status": "ok"}


@router.get("/ready", include_in_schema=True)
async def ready() -> dict[str, str]:
    """Return readiness information for the service."""
    return {"status": "ready"}


@router.get("/live", include_in_schema=True)
async def live() -> dict[str, str]:
    """Return liveness information for the service."""
    return {"status": "alive"}
