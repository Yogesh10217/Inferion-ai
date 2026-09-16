"""Structured Business Case Evaluation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.portfolio_platform.exceptions import (
    BusinessCaseNotFoundException,
    CrossTenantPortfolioAccessException,
)


class BusinessCaseStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class CostEstimate(BaseModel):
    implementation_cost_usd: float = 50000.0
    annual_operating_cost_usd: float = 12000.0
    infrastructure_cost_usd: float = 8000.0


class BenefitEstimate(BaseModel):
    annual_revenue_usd: float = 150000.0
    annual_cost_savings_usd: float = 50000.0
    productivity_value_usd: float = 30000.0


class ROIProjection(BaseModel):
    estimated_roi_percentage: float = 180.0
    net_present_value_usd: float = 120000.0
    payback_period_months: float = 8.5
    confidence_score: float = 90.0  # 0 to 100


class BusinessCase(BaseModel):
    business_case_id: str = Field(default_factory=lambda: f"bc_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    initiative_id: str
    problem_statement: str
    status: BusinessCaseStatus = BusinessCaseStatus.SUBMITTED
    costs: CostEstimate = Field(default_factory=CostEstimate)
    benefits: BenefitEstimate = Field(default_factory=BenefitEstimate)
    roi_projection: ROIProjection = Field(default_factory=ROIProjection)
    architecture_trust_score: float = 90.0
    data_trust_score: float = 95.0
    compliance_score: float = 90.0
    risk_score: float = 20.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def sanitize_metadata(self) -> None:
        """Sanitize secrets and credentials from business case metadata."""
        secret_keys = {"password", "secret", "token", "api_key", "credentials", "private_key", "ssn"}
        sanitized = {}
        for k, v in self.metadata.items():
            if any(sk in k.lower() for sk in secret_keys):
                sanitized[k] = "[REDACTED]"
            else:
                sanitized[k] = v
        self.metadata = sanitized


class BusinessCaseManager:
    """Manages creation, evaluation, and sanitization of initiative business cases."""

    def __init__(self) -> None:
        self._business_cases: Dict[str, BusinessCase] = {}

    def create_business_case(
        self,
        tenant_id: str,
        initiative_id: str,
        problem_statement: str,
        costs: Optional[CostEstimate] = None,
        benefits: Optional[BenefitEstimate] = None,
        architecture_trust_score: float = 90.0,
        data_trust_score: float = 95.0,
        compliance_score: float = 90.0,
        risk_score: float = 20.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> BusinessCase:
        c_est = costs or CostEstimate()
        b_est = benefits or BenefitEstimate()

        total_cost = c_est.implementation_cost_usd + c_est.annual_operating_cost_usd
        total_benefit = b_est.annual_revenue_usd + b_est.annual_cost_savings_usd + b_est.productivity_value_usd
        net_benefit = total_benefit - total_cost

        roi_pct = (net_benefit / max(1.0, total_cost)) * 100.0
        payback_m = (total_cost / max(1.0, total_benefit)) * 12.0

        roi_proj = ROIProjection(
            estimated_roi_percentage=max(0.0, roi_pct),
            net_present_value_usd=net_benefit,
            payback_period_months=max(0.1, payback_m),
            confidence_score=min(architecture_trust_score, data_trust_score, compliance_score),
        )

        bc = BusinessCase(
            tenant_id=tenant_id,
            initiative_id=initiative_id,
            problem_statement=problem_statement,
            costs=c_est,
            benefits=b_est,
            roi_projection=roi_proj,
            architecture_trust_score=architecture_trust_score,
            data_trust_score=data_trust_score,
            compliance_score=compliance_score,
            risk_score=risk_score,
            metadata=metadata or {},
        )
        bc.sanitize_metadata()
        self._business_cases[bc.business_case_id] = bc
        return bc

    def get_business_case(self, business_case_id: str, tenant_id: str) -> BusinessCase:
        bc = self._business_cases.get(business_case_id)
        if not bc:
            raise BusinessCaseNotFoundException(business_case_id=business_case_id, tenant_id=tenant_id)
        if bc.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantPortfolioAccessException(request_tenant=tenant_id, target_tenant=bc.tenant_id, resource_id=business_case_id)
        return bc

    def get_by_initiative(self, initiative_id: str, tenant_id: str) -> Optional[BusinessCase]:
        for bc in self._business_cases.values():
            if bc.initiative_id == initiative_id and (bc.tenant_id == tenant_id or tenant_id == "global"):
                return bc
        return None
