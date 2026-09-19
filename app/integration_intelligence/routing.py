"""Integration Routing Intelligence & Circuit Breaker Reuse (Phase 5.40)."""

import uuid
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class RoutingStrategy(str, Enum):
    PRIMARY = "PRIMARY"
    FALLBACK = "FALLBACK"
    REGIONAL = "REGIONAL"
    DEGRADED = "DEGRADED"
    WEIGHTED = "WEIGHTED"


class RouteHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"


class IntegrationRoute(BaseModel):
    """Integration Route Representation."""

    route_id: str = Field(default_factory=lambda: f"route_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_connector_id: str
    target_endpoint_id: str
    strategy: RoutingStrategy = RoutingStrategy.PRIMARY
    priority: int = 1
    health: RouteHealth = RouteHealth.HEALTHY
    is_active: bool = True


class RouteDecision(BaseModel):
    """Outcome of routing decision."""

    decision_id: str = Field(default_factory=lambda: f"route_dec_{uuid.uuid4().hex[:8]}")
    selected_route_id: str
    selected_connector_id: str
    selected_endpoint_id: str
    strategy_used: RoutingStrategy
    reason: str


class IntegrationRoutingManager:
    """Manages integration routing strategies with fallback capabilities."""

    def __init__(self) -> None:
        self._routes: Dict[str, IntegrationRoute] = {}

    def register_route(
        self,
        tenant_id: str,
        target_connector_id: str,
        target_endpoint_id: str,
        strategy: RoutingStrategy = RoutingStrategy.PRIMARY,
        priority: int = 1,
    ) -> IntegrationRoute:
        route = IntegrationRoute(
            tenant_id=tenant_id,
            target_connector_id=target_connector_id,
            target_endpoint_id=target_endpoint_id,
            strategy=strategy,
            priority=priority,
        )
        self._routes[route.route_id] = route
        return route

    def resolve_route(self, tenant_id: str, connector_id: str) -> RouteDecision:
        routes = [
            r
            for r in self._routes.values()
            if r.tenant_id == tenant_id and r.target_connector_id == connector_id and r.is_active
        ]

        healthy_primary = [
            r for r in routes if r.strategy == RoutingStrategy.PRIMARY and r.health == RouteHealth.HEALTHY
        ]
        if healthy_primary:
            best = min(healthy_primary, key=lambda x: x.priority)
            return RouteDecision(
                selected_route_id=best.route_id,
                selected_connector_id=best.target_connector_id,
                selected_endpoint_id=best.target_endpoint_id,
                strategy_used=RoutingStrategy.PRIMARY,
                reason="Selected healthy primary route.",
            )

        # Fallback route
        fallbacks = [r for r in routes if r.strategy == RoutingStrategy.FALLBACK and r.health != RouteHealth.FAILED]
        if fallbacks:
            best = min(fallbacks, key=lambda x: x.priority)
            return RouteDecision(
                selected_route_id=best.route_id,
                selected_connector_id=best.target_connector_id,
                selected_endpoint_id=best.target_endpoint_id,
                strategy_used=RoutingStrategy.FALLBACK,
                reason="Primary route degraded or failed. Selected fallback route.",
            )

        # Degraded route
        if routes:
            return RouteDecision(
                selected_route_id=routes[0].route_id,
                selected_connector_id=routes[0].target_connector_id,
                selected_endpoint_id=routes[0].target_endpoint_id,
                strategy_used=RoutingStrategy.DEGRADED,
                reason="Routes degraded. Operating under degraded strategy.",
            )

        return RouteDecision(
            selected_route_id="default",
            selected_connector_id=connector_id,
            selected_endpoint_id="ep_default",
            strategy_used=RoutingStrategy.PRIMARY,
            reason="Default routing fallback.",
        )

    def get_route(self, tenant_id: str, route_id: str) -> IntegrationRoute:
        route = self._routes.get(route_id)
        if not route or route.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return route
