from typing import Optional
from app.routing.routing_strategy import RoutingStrategy
from app.registry.model_metadata import ModelMetadata
from app.routing.request_router import RoutingRequest
from .decision_engine import DecisionEngine
from .routing_context import RoutingContext


class DecisionEngineRoutingStrategy(RoutingStrategy):
    """Adapter strategy connecting the DecisionEngine pipeline to the legacy RoutingStrategy interface."""

    def __init__(self, engine: Optional[DecisionEngine] = None):
        self.engine = engine or DecisionEngine()

    async def determine_provider_name(
        self,
        *,
        model: Optional[ModelMetadata] = None,
        request: Optional[RoutingRequest] = None,
    ) -> str:
        req_meta = request.metadata if request and hasattr(request, "metadata") and request.metadata else {}
        context = RoutingContext(
            request_metadata=req_meta,
            organization_id=req_meta.get("organization_id"),
            workspace_id=req_meta.get("workspace_id"),
            user_id=req_meta.get("user_id"),
            required_capabilities=req_meta.get("capabilities", []),
        )
        model_id = model.id if model and hasattr(model, "id") else "unknown"
        provider_name = self.engine.decide(model_id, context)
        return provider_name
