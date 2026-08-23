"""Portfolio Aggregations & Health Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import (
    PortfolioNotFoundException,
    CrossTenantPortfolioAccessException,
)


class PortfolioStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class PortfolioHealth(str, Enum):
    HEALTHY = "HEALTHY"
    NEEDS_ATTENTION = "NEEDS_ATTENTION"
    AT_RISK = "AT_RISK"
    CRITICAL = "CRITICAL"


class Portfolio(BaseModel):
    portfolio_id: str = Field(default_factory=lambda: f"port_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    description: str
    status: PortfolioStatus = PortfolioStatus.ACTIVE
    health: PortfolioHealth = PortfolioHealth.HEALTHY
    initiative_ids: List[str] = Field(default_factory=list)
    total_budget_allocated_usd: float = 0.0
    total_realized_value_usd: float = 0.0
    aggregate_roi_percentage: float = 0.0
    architecture_trust_score: float = 90.0
    data_trust_score: float = 95.0
    compliance_score: float = 90.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioManager:
    """Aggregates initiatives, investments, value, and health scores into enterprise portfolios."""

    def __init__(self) -> None:
        self._portfolios: Dict[str, Portfolio] = {}

    def create_portfolio(self, tenant_id: str, name: str, description: str) -> Portfolio:
        port = Portfolio(tenant_id=tenant_id, name=name, description=description)
        self._portfolios[port.portfolio_id] = port
        return port

    def get_portfolio(self, portfolio_id: str, tenant_id: str) -> Portfolio:
        port = self._portfolios.get(portfolio_id)
        if not port:
            raise PortfolioNotFoundException(portfolio_id=portfolio_id, tenant_id=tenant_id)
        if port.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(request_tenant=tenant_id, target_tenant=port.tenant_id, resource_id=portfolio_id)
        return port

    def add_initiative(self, portfolio_id: str, tenant_id: str, initiative_id: str) -> Portfolio:
        port = self.get_portfolio(portfolio_id, tenant_id)
        if initiative_id not in port.initiative_ids:
            port.initiative_ids.append(initiative_id)
        return port

    def list_portfolios(self, tenant_id: str) -> List[Portfolio]:
        return [p for p in self._portfolios.values() if p.tenant_id in (tenant_id, "global")]
