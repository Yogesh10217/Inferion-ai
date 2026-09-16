"""Decision Risk Composition Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.governance_platform.risk import RiskManager


class DecisionRiskDimension(str, Enum):
    ARCHITECTURE = "ARCHITECTURE"
    COMPLIANCE = "COMPLIANCE"
    DATA_GOVERNANCE = "DATA_GOVERNANCE"
    PORTFOLIO = "PORTFOLIO"
    OPERATIONS = "OPERATIONS"
    SECURITY = "SECURITY"


class DecisionRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"riskprof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    overall_risk_score: float = 20.0
    overall_risk_level: str = "LOW"
    dimension_risks: Dict[DecisionRiskDimension, float] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionRiskManager:
    """Aggregates multi-platform risk signals using existing RiskManager."""

    def __init__(self, risk_manager: Optional[RiskManager] = None) -> None:
        self.risk_manager = risk_manager or RiskManager()

    def evaluate_decision_risk(
        self,
        tenant_id: str,
        context_id: str,
        architecture_risk: Optional[float] = None,
        compliance_risk: Optional[float] = None,
        data_risk: Optional[float] = None,
        portfolio_risk: Optional[float] = None,
        ops_risk: Optional[float] = None,
        sec_risk: Optional[float] = None,
    ) -> DecisionRiskProfile:
        dim_risks: Dict[DecisionRiskDimension, float] = {}

        if architecture_risk is not None:
            dim_risks[DecisionRiskDimension.ARCHITECTURE] = architecture_risk
        if compliance_risk is not None:
            dim_risks[DecisionRiskDimension.COMPLIANCE] = compliance_risk
        if data_risk is not None:
            dim_risks[DecisionRiskDimension.DATA_GOVERNANCE] = data_risk
        if portfolio_risk is not None:
            dim_risks[DecisionRiskDimension.PORTFOLIO] = portfolio_risk
        if ops_risk is not None:
            dim_risks[DecisionRiskDimension.OPERATIONS] = ops_risk
        if sec_risk is not None:
            dim_risks[DecisionRiskDimension.SECURITY] = sec_risk

        if not dim_risks:
            dim_risks = {
                DecisionRiskDimension.ARCHITECTURE: 20.0,
                DecisionRiskDimension.COMPLIANCE: 20.0,
                DecisionRiskDimension.DATA_GOVERNANCE: 20.0,
                DecisionRiskDimension.PORTFOLIO: 20.0,
                DecisionRiskDimension.OPERATIONS: 20.0,
                DecisionRiskDimension.SECURITY: 20.0,
            }

        max_risk = max(dim_risks.values())
        avg_risk = sum(dim_risks.values()) / len(dim_risks)
        overall = (max_risk * 0.6) + (avg_risk * 0.4)

        if overall >= 75.0:
            level = "CRITICAL"
        elif overall >= 50.0:
            level = "HIGH"
        elif overall >= 25.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        return DecisionRiskProfile(
            tenant_id=tenant_id,
            context_id=context_id,
            overall_risk_score=round(overall, 2),
            overall_risk_level=level,
            dimension_risks=dim_risks,
        )
