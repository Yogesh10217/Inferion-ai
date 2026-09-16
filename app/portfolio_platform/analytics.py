"""Tenant-Scoped Portfolio Analytics Subsystem."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.portfolio_platform.funding import FundingManager
from app.portfolio_platform.initiatives import InitiativeManager
from app.portfolio_platform.investment import InvestmentManager
from app.portfolio_platform.strategy import StrategyManager
from app.portfolio_platform.trust import PortfolioTrustEngine


class PortfolioInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"portins_{uuid.uuid4().hex[:12]}")
    title: str
    description: str
    impact_level: str = "MEDIUM"


class PortfolioReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"portrep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    total_initiatives_count: int = 0
    total_allocated_funding_usd: float = 0.0
    remaining_budget_usd: float = 500000.0
    overall_trust_score: float = 90.0
    insights: List[PortfolioInsight] = Field(default_factory=list)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioAnalyticsEngine:
    """Generates tenant-isolated portfolio intelligence reports."""

    def __init__(
        self,
        strategy_manager: StrategyManager,
        initiative_manager: InitiativeManager,
        investment_manager: InvestmentManager,
        funding_manager: FundingManager,
        trust_engine: PortfolioTrustEngine,
    ) -> None:
        self.strategy_manager = strategy_manager
        self.initiative_manager = initiative_manager
        self.investment_manager = investment_manager
        self.funding_manager = funding_manager
        self.trust_engine = trust_engine

    def generate_report(self, tenant_id: str) -> PortfolioReport:
        inits = self.initiative_manager.list_initiatives(tenant_id)
        envelope = self.funding_manager.get_budget_envelope(tenant_id)
        trust = self.trust_engine.get_trust_score(tenant_id)

        insights = []
        if len(inits) > 0:
            insights.append(
                PortfolioInsight(
                    title="Active AI Initiative Pipeline",
                    description=f"Managing {len(inits)} AI initiative(s) across stages.",
                    impact_level="HIGH",
                )
            )

        return PortfolioReport(
            tenant_id=tenant_id,
            total_initiatives_count=len(inits),
            total_allocated_funding_usd=envelope.allocated_budget_usd,
            remaining_budget_usd=envelope.remaining_budget_usd,
            overall_trust_score=trust.overall_score,
            insights=insights,
        )
