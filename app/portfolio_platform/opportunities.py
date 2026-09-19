"""AI Opportunity Discovery & Qualification Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import CrossTenantPortfolioAccessException


class OpportunityType(str, Enum):
    AUTOMATION = "AUTOMATION"
    INTELLIGENCE_AUGMENTATION = "INTELLIGENCE_AUGMENTATION"
    NEW_CAPABILITY = "NEW_CAPABILITY"
    COST_REDUCTION = "COST_REDUCTION"
    RISK_MITIGATION = "RISK_MITIGATION"


class OpportunitySource(str, Enum):
    BUSINESS_REQUEST = "BUSINESS_REQUEST"
    OPERATIONAL_SIGNAL = "OPERATIONAL_SIGNAL"
    INTELLIGENCE_RECOMMENDATION = "INTELLIGENCE_RECOMMENDATION"
    CUSTOMER_FEEDBACK = "CUSTOMER_FEEDBACK"
    INCIDENT_ANALYSIS = "INCIDENT_ANALYSIS"
    COST_OPTIMIZATION = "COST_OPTIMIZATION"
    COMPLIANCE_FINDING = "COMPLIANCE_FINDING"
    ARCHITECTURE_ANALYSIS = "ARCHITECTURE_ANALYSIS"
    MANUAL_DISCOVERY = "MANUAL_DISCOVERY"


class OpportunityStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    QUALIFYING = "QUALIFYING"
    QUALIFIED = "QUALIFIED"
    REJECTED = "REJECTED"
    CONVERTED_TO_INITIATIVE = "CONVERTED_TO_INITIATIVE"


class OpportunityValuePotential(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    TRANSFORMATIONAL = "TRANSFORMATIONAL"


class AIOpportunity(BaseModel):
    opportunity_id: str = Field(default_factory=lambda: f"opp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    description: str
    source: OpportunitySource = OpportunitySource.MANUAL_DISCOVERY
    opportunity_type: OpportunityType = OpportunityType.NEW_CAPABILITY
    status: OpportunityStatus = OpportunityStatus.DISCOVERED
    value_potential: OpportunityValuePotential = OpportunityValuePotential.HIGH
    converted_initiative_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OpportunityManager:
    """Manages AI opportunity discovery, qualification, and conversion to initiatives."""

    def __init__(self) -> None:
        self._opportunities: Dict[str, AIOpportunity] = {}

    def discover_opportunity(
        self,
        tenant_id: str,
        title: str,
        description: str,
        source: OpportunitySource = OpportunitySource.MANUAL_DISCOVERY,
        opportunity_type: OpportunityType = OpportunityType.NEW_CAPABILITY,
        value_potential: OpportunityValuePotential = OpportunityValuePotential.HIGH,
    ) -> AIOpportunity:
        opp = AIOpportunity(
            tenant_id=tenant_id,
            title=title,
            description=description,
            source=source,
            opportunity_type=opportunity_type,
            value_potential=value_potential,
        )
        self._opportunities[opp.opportunity_id] = opp
        return opp

    def get_opportunity(self, opportunity_id: str, tenant_id: str) -> AIOpportunity:
        opp = self._opportunities.get(opportunity_id)
        if not opp:
            raise KeyError(f"Opportunity '{opportunity_id}' not found.")
        if opp.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(
                request_tenant=tenant_id, target_tenant=opp.tenant_id, resource_id=opportunity_id
            )
        return opp

    def qualify_opportunity(self, opportunity_id: str, tenant_id: str, is_qualified: bool = True) -> AIOpportunity:
        opp = self.get_opportunity(opportunity_id, tenant_id)
        opp.status = OpportunityStatus.QUALIFIED if is_qualified else OpportunityStatus.REJECTED
        return opp

    def mark_converted(self, opportunity_id: str, tenant_id: str, initiative_id: str) -> AIOpportunity:
        opp = self.get_opportunity(opportunity_id, tenant_id)
        opp.status = OpportunityStatus.CONVERTED_TO_INITIATIVE
        opp.converted_initiative_id = initiative_id
        return opp

    def list_opportunities(self, tenant_id: str) -> List[AIOpportunity]:
        return [o for o in self._opportunities.values() if o.tenant_id in (tenant_id, "global")]
