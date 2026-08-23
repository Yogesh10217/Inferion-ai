"""Decision Risk Composition Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
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
        architecture_risk: float = 20.0,
        compliance_risk: float = 20.0,
        data_risk: float = 20.0,
        portfolio_risk: float = 20.0,
        ops_risk: float = 20.0,
        sec_risk: float = 20.0,
    ) -> DecisionRiskProfile:
        dim_risks = {
            DecisionRiskDimension.ARCHITECTURE: architecture_risk,
            DecisionRiskDimension.COMPLIANCE: compliance_risk,
            DecisionRiskDimension.DATA_GOVERNANCE: data_risk,
            DecisionRiskDimension.PORTFOLIO: portfolio_risk,
            DecisionRiskDimension.OPERATIONS: ops_risk,
            DecisionRiskDimension.SECURITY: sec_risk,
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
            overall_risk_score=overall,
            overall_risk_level=level,
            dimension_risks=dim_risks,
        )
