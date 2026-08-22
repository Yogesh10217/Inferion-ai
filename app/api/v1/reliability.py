"""FastAPI Router for Platform Reliability & Service Health (/v1/reliability)."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from app.reliability.health import SystemHealthManager
from app.resilience.circuit_breaker import CircuitBreakerRegistry

router = APIRouter(prefix="/v1/reliability", tags=["reliability"])

_global_health_manager = SystemHealthManager()
_global_circuit_registry = CircuitBreakerRegistry()


def get_health_manager() -> SystemHealthManager:
    return _global_health_manager


def get_circuit_registry() -> CircuitBreakerRegistry:
    return _global_circuit_registry


@router.get("/health")
async def get_system_health(health_mgr: SystemHealthManager = Depends(get_health_manager)):
    """Retrieve full system readiness and health."""
    return await health_mgr.check_readiness()


@router.get("/dependencies")
async def get_dependency_health(health_mgr: SystemHealthManager = Depends(get_health_manager)):
    """Retrieve dependency health breakdown."""
    deps = await health_mgr.check_dependencies()
    return {"status": "ok", "dependencies": deps}


@router.get("/circuit-breakers")
async def get_circuit_breakers(registry: CircuitBreakerRegistry = Depends(get_circuit_registry)):
    """Retrieve status of all circuit breakers."""
    breakers = registry.list_breakers()
    return {"circuit_breakers": breakers}
