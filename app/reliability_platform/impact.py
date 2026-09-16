"""Architecture & Business Impact Analysis Subsystem (Phase 5.31)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.architecture_platform.manager import ArchitecturePlatformManager
from app.portfolio_platform.manager import PortfolioPlatformManager


class ImpactLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ReliabilityImpactAnalysis(BaseModel):
    analysis_id: str = Field(default_factory=lambda: f"imp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    service_id: str
    affected_components: List[str] = Field(default_factory=list)
    affected_initiatives: List[str] = Field(default_factory=list)
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    estimated_financial_loss_usd: float = 0.0
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ImpactAnalyzer:
    """Analyzes architecture topology dependencies and portfolio strategic impact during outages."""

    def __init__(
        self,
        architecture_manager: Optional[ArchitecturePlatformManager] = None,
        portfolio_manager: Optional[PortfolioPlatformManager] = None,
    ) -> None:
        self.architecture_manager = architecture_manager or ArchitecturePlatformManager()
        self.portfolio_manager = portfolio_manager or PortfolioPlatformManager()

    def analyze_impact(self, tenant_id: str, service_id: str) -> ReliabilityImpactAnalysis:
        # Check architecture nodes
        nodes = self.architecture_manager.node_manager.list_nodes(tenant_id)
        affected_nodes = [n.node_id for n in nodes if n.metadata.resource_id == service_id or service_id in n.name]

        # Check portfolio strategies
        strategies = self.portfolio_manager.strategy_manager.list_strategies(tenant_id)
        affected_strats = [s.strategy_id for s in strategies]

        impact_lvl = ImpactLevel.HIGH if len(affected_nodes) > 1 else ImpactLevel.MEDIUM

        return ReliabilityImpactAnalysis(
            tenant_id=tenant_id,
            service_id=service_id,
            affected_components=affected_nodes or ["node_default_service"],
            affected_initiatives=affected_strats,
            impact_level=impact_lvl,
            estimated_financial_loss_usd=5000.0,
        )
