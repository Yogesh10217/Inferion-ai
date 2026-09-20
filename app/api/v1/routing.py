from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.routing.decision_engine import DecisionEngine
from app.routing.routing_context import RoutingContext
from app.routing.routing_policy import RoutingPolicy

router = APIRouter(prefix="/routing", tags=["routing"])

# Shared singleton DecisionEngine instance for Admin APIs
_global_engine = DecisionEngine()


def get_engine() -> DecisionEngine:
    return _global_engine


class PolicyCreateSchema(BaseModel):
    name: str
    weights: Optional[Dict[str, float]] = None
    priority: int = 10
    description: str = ""
    organization_id: Optional[str] = None
    is_default: bool = False


class PolicyUpdateSchema(BaseModel):
    weights: Optional[Dict[str, float]] = None
    priority: Optional[int] = None
    description: Optional[str] = None


@router.get("/policies")
async def get_policies(engine: DecisionEngine = Depends(get_engine)):
    """List active routing policies."""
    policies = engine.policy_registry.list_policies()
    return {"policies": [p.to_dict() for p in policies]}


@router.post("/policies", status_code=status.HTTP_201_CREATED)
async def create_policy(data: PolicyCreateSchema, engine: DecisionEngine = Depends(get_engine)):
    """Create a new routing policy."""
    policy = RoutingPolicy(
        name=data.name,
        weights=data.weights,
        priority=data.priority,
        description=data.description,
        organization_id=data.organization_id,
        is_default=data.is_default,
    )
    engine.policy_registry.add_policy(policy)
    return {"status": "created", "policy": policy.to_dict()}


@router.patch("/policies/{id}")
async def update_policy(
    id: str,
    data: PolicyUpdateSchema,
    engine: DecisionEngine = Depends(get_engine),
):
    """Update an existing routing policy by name/id."""
    existing = engine.policy_registry.get_policy(id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy '{id}' not found")
    if data.weights is not None:
        existing.weights = existing._normalize_weights(data.weights)
    if data.priority is not None:
        existing.priority = data.priority
    if data.description is not None:
        existing.description = data.description
    return {"status": "updated", "policy": existing.to_dict()}


@router.delete("/policies/{id}")
async def delete_policy(id: str, engine: DecisionEngine = Depends(get_engine)):
    """Delete a routing policy."""
    success = engine.policy_registry.remove_policy(id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy '{id}' not found")
    return {"status": "deleted", "id": id}


@router.get("/rankings")
async def get_provider_rankings(
    policy_name: str = "default",
    engine: DecisionEngine = Depends(get_engine),
):
    """Get calculated provider rankings for a policy."""
    policy = engine.policy_registry.get_policy(policy_name)
    if not policy:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Policy '{policy_name}' not found")

    providers = ["openai_provider", "anthropic_provider", "mock_provider"]
    rankings = engine.ranker.rank(
        providers=providers,
        policy=policy,
        metrics=engine.metrics,
        health_status={"openai_provider": True, "anthropic_provider": True, "mock_provider": True},
    )
    return {
        "policy": policy_name,
        "rankings": [{"provider": p, "score": s} for p, s in rankings],
    }


@router.get("/cache")
async def get_cache_stats(engine: DecisionEngine = Depends(get_engine)):
    """Retrieve cache hit/miss statistics and active sizes."""
    return engine.cache.get_stats()


@router.post("/cache/invalidate")
async def invalidate_cache(engine: DecisionEngine = Depends(get_engine)):
    """Flush all routing caches."""
    engine.cache.invalidate_all()
    return {"status": "invalidated"}


@router.get("/metrics")
async def get_metrics(engine: DecisionEngine = Depends(get_engine)):
    """Retrieve provider statistics and latency/success rate metrics."""
    return {"provider_metrics": engine.metrics.get_all_stats()}


@router.get("/capabilities")
async def get_capabilities(engine: DecisionEngine = Depends(get_engine)):
    """Retrieve registered provider capabilities."""
    return {"capabilities": engine.capability_registry.get_all()}


@router.get("/health")
async def get_routing_health(engine: DecisionEngine = Depends(get_engine)):
    """Retrieve routing engine status and provider health map."""
    providers = ["openai_provider", "anthropic_provider", "mock_provider"]
    health_map = {p: engine.cache.get_health(p) or True for p in providers}
    return {
        "status": "healthy",
        "provider_health": health_map,
        "active_policies_count": len(engine.policy_registry.list_policies()),
    }


@router.post("/decide")
async def evaluate_decision(
    model_id: str,
    capabilities: Optional[List[str]] = None,
    engine: DecisionEngine = Depends(get_engine),
):
    """Simulate a routing decision and return the decision trace explanation."""
    ctx = RoutingContext(required_capabilities=capabilities or [])
    selected = engine.decide(model_id, ctx)
    return {
        "selected_provider": selected,
        "decision_explanation": ctx.decision_explanation,
        "trace": ctx.get_full_trace(),
    }
