"""Business and Technical Impact Analysis (Phase 5.41)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException


class BusinessImpact(str, Enum):
    CRITICAL_PROCESS_HALT = "CRITICAL_PROCESS_HALT"
    REVENUE_LOSS = "REVENUE_LOSS"
    COMPLIANCE_VIOLATION = "COMPLIANCE_VIOLATION"
    MINOR = "MINOR"


class TechnicalImpact(str, Enum):
    SERVICE_OUTAGE = "SERVICE_OUTAGE"
    LATENCY_SPIKE = "LATENCY_SPIKE"
    DATA_CORRUPTION = "DATA_CORRUPTION"
    DEGRADED_PERFORMANCE = "DEGRADED_PERFORMANCE"


class OperationalImpact(BaseModel):
    impact_id: str = Field(default_factory=lambda: f"imp_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    incident_id: str
    business_impact: BusinessImpact = BusinessImpact.MINOR
    technical_impact: TechnicalImpact = TechnicalImpact.DEGRADED_PERFORMANCE
    affected_services: List[str] = Field(default_factory=list)
    affected_regions: List[str] = Field(default_factory=list)
    estimated_user_count: int = 0
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ImpactAnalysisManager:
    """Manages operational impact calculations across business and technical dimensions."""

    def __init__(self) -> None:
        self._impacts: Dict[str, OperationalImpact] = {}

    def analyze_impact(
        self,
        tenant_id: str,
        incident_id: str,
        affected_services: List[str],
        business_impact: BusinessImpact = BusinessImpact.MINOR,
        technical_impact: TechnicalImpact = TechnicalImpact.DEGRADED_PERFORMANCE,
        affected_regions: Optional[List[str]] = None,
        estimated_user_count: int = 100,
    ) -> OperationalImpact:
        imp = OperationalImpact(
            tenant_id=tenant_id,
            incident_id=incident_id,
            business_impact=business_impact,
            technical_impact=technical_impact,
            affected_services=affected_services,
            affected_regions=affected_regions or ["us-east-1"],
            estimated_user_count=estimated_user_count,
        )
        self._impacts[imp.impact_id] = imp
        return imp

    def get_impact(self, tenant_id: str, impact_id: str) -> OperationalImpact:
        imp = self._impacts.get(impact_id)
        if not imp or imp.tenant_id != tenant_id:
            raise CrossTenantOperationsAccessException()
        return imp
