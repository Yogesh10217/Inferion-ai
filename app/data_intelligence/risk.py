"""Data risk intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException


class DataRiskDimension(str, Enum):
    QUALITY_RISK = "QUALITY_RISK"
    FRESHNESS_RISK = "FRESHNESS_RISK"
    SECURITY_RISK = "SECURITY_RISK"
    COMPLIANCE_RISK = "COMPLIANCE_RISK"
    PIPELINE_RISK = "PIPELINE_RISK"
    DOWNSTREAM_IMPACT_RISK = "DOWNSTREAM_IMPACT_RISK"


class DataRiskProfile(BaseModel):
    profile_id: str
    dataset_id: str
    tenant_id: str
    overall_risk_score: float  # 0.0 - 100.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    dimensions: Dict[DataRiskDimension, float]


class DataRiskAssessment(BaseModel):
    assessment_id: str
    dataset_id: str
    tenant_id: str
    profile: DataRiskProfile
    summary: str
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataRiskManager:
    """Evaluates comprehensive data risks across dimensions."""

    def evaluate_risk(
        self,
        dataset_id: str,
        tenant_id: str,
        quality_risk: float = 10.0,
        freshness_risk: float = 15.0,
        security_risk: float = 20.0,
        compliance_risk: float = 10.0,
        pipeline_risk: float = 10.0,
        downstream_risk: float = 15.0,
    ) -> DataRiskAssessment:
        pid = f"risk-prof-{uuid.uuid4().hex[:8]}"
        aid = f"risk-ass-{uuid.uuid4().hex[:8]}"

        dims = {
            DataRiskDimension.QUALITY_RISK: quality_risk,
            DataRiskDimension.FRESHNESS_RISK: freshness_risk,
            DataRiskDimension.SECURITY_RISK: security_risk,
            DataRiskDimension.COMPLIANCE_RISK: compliance_risk,
            DataRiskDimension.PIPELINE_RISK: pipeline_risk,
            DataRiskDimension.DOWNSTREAM_IMPACT_RISK: downstream_risk,
        }

        overall = round(sum(dims.values()) / len(dims), 2)
        risk_lvl = "CRITICAL" if overall >= 75.0 else ("HIGH" if overall >= 50.0 else ("MEDIUM" if overall >= 25.0 else "LOW"))

        prof = DataRiskProfile(
            profile_id=pid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            overall_risk_score=overall,
            risk_level=risk_lvl,
            dimensions=dims,
        )

        return DataRiskAssessment(
            assessment_id=aid,
            dataset_id=dataset_id,
            tenant_id=tenant_id,
            profile=prof,
            summary=f"Data risk assessment for dataset {dataset_id}: overall={overall:.1f} ({risk_lvl})",
        )
