from app.routing.routing_strategy import RoutingStrategy
from app.registry.model_metadata import ModelMetadata
from app.routing.request_router import RoutingRequest
from .decision_engine import DecisionEngine
from .routing_context import RoutingContext

class DecisionEngineRoutingStrategy(RoutingStrategy):
    def __init__(self, engine: DecisionEngine):
        self.engine = engine

    async def determine_provider_name(self, *, model: ModelMetadata | None, request: RoutingRequest | None = None) -> str:
        context = RoutingContext(request_metadata=request.metadata if request else {})
        provider_id = self.engine.decide(model.id if model else "unknown", context)
        return provider_id or "default_provider"
