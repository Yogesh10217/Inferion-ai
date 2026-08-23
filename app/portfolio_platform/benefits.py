"""Benefits Realization Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import (
    BenefitsRealizationException,
    CrossTenantPortfolioAccessException,
)


class BenefitType(str, Enum):
    FINANCIAL = "FINANCIAL"
    OPERATIONAL = "OPERATIONAL"
    STRATEGIC = "STRATEGIC"
    COMPLIANCE = "COMPLIANCE"


class BenefitStatus(str, Enum):
    PLANNED = "PLANNED"
    TRACKING = "TRACKING"
    PARTIALLY_REALIZED = "PARTIALLY_REALIZED"
    REALIZED = "REALIZED"
    UNDERPERFORMING = "UNDERPERFORMING"
    NOT_REALIZED = "NOT_REALIZED"


class Benefit(BaseModel):
    benefit_id: str = Field(default_factory=lambda: f"ben_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    title: str
    benefit_type: BenefitType = BenefitType.FINANCIAL
    status: BenefitStatus = BenefitStatus.PLANNED
    expected_value_usd: float
    realized_value_usd: float = 0.0
    realization_percentage: float = 0.0
    deviation_usd: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class BenefitsManager:
    """Tracks and calculates benefits realization for AI initiatives."""

    def __init__(self) -> None:
        self._benefits: Dict[str, Benefit] = {}

    def create_benefit_plan(
        self,
        tenant_id: str,
        initiative_id: str,
        title: str,
        expected_value_usd: float,
        benefit_type: BenefitType = BenefitType.FINANCIAL,
    ) -> Benefit:
        benefit = Benefit(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            title=title,
            expected_value_usd=expected_value_usd,
            benefit_type=benefit_type,
            status=BenefitStatus.PLANNED,
        )
        self._benefits[benefit.benefit_id] = benefit
        return benefit

    def record_realized_benefit(self, benefit_id: str, tenant_id: str, realized_value_usd: float) -> Benefit:
        b = self.get_benefit(benefit_id, tenant_id)
        b.realized_value_usd = realized_value_usd
        b.realization_percentage = (realized_value_usd / max(1.0, b.expected_value_usd)) * 100.0
        b.deviation_usd = realized_value_usd - b.expected_value_usd

        if b.realization_percentage >= 95.0:
            b.status = BenefitStatus.REALIZED
        elif b.realization_percentage >= 50.0:
            b.status = BenefitStatus.PARTIALLY_REALIZED
        elif b.realization_percentage > 0.0:
            b.status = BenefitStatus.UNDERPERFORMING
        else:
            b.status = BenefitStatus.NOT_REALIZED

        b.updated_at = datetime.now(timezone.utc)
        return b

    def get_benefit(self, benefit_id: str, tenant_id: str) -> Benefit:
        b = self._benefits.get(benefit_id)
        if not b:
            raise BenefitsRealizationException(f"Benefit '{benefit_id}' not found.")
        if b.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(request_tenant=tenant_id, target_tenant=b.tenant_id, resource_id=benefit_id)
        return b

    def list_benefits_for_initiative(self, tenant_id: str, initiative_id: str) -> List[Benefit]:
        return [b for b in self._benefits.values() if b.tenant_id == tenant_id and b.initiative_id == initiative_id]
