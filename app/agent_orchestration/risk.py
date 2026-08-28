"""Agent Risk Composition Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.risk import RiskReference, RiskAssessmentReference
from app.agent_orchestration.exceptions import CrossTenantAgentAccessException


class AgentRiskDimension(str, Enum):
    AUTONOMY_LEVEL = "AUTONOMY_LEVEL"
    TARGET_SENSITIVITY = "TARGET_SENSITIVITY"
    ACTION_REVERSIBILITY = "ACTION_REVERSIBILITY"
    TOOL_PRIVILEGE = "TOOL_PRIVILEGE"
    DATA_SENSITIVITY = "DATA_SENSITIVITY"
    HISTORICAL_FAILURES = "HISTORICAL_FAILURES"
    FINANCIAL_IMPACT = "FINANCIAL_IMPACT"


class AgentRiskProfile(BaseModel):
    agent_id: str
    tenant_id: str
    base_risk_score: float = 0.2
    max_allowed_risk: float = 0.8
    risk_level: str = "LOW"


class AgentRiskAssessment(BaseModel):
    risk_id: str = Field(default_factory=lambda: f"agrisk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    composite_score: float = 0.25
    level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    requires_approval: bool = False
    dimension_scores: Dict[str, float] = Field(default_factory=dict)
    mitigations: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRiskManager:
    """Composes agent risk dimensions to compute comprehensive risk profiles for tasks and actions."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._assessments: Dict[str, AgentRiskAssessment] = {}

    def evaluate_task_risk(
        self,
        tenant_id: str,
        agent_id: str,
        task_id: str,
        proposed_action: str,
        target_system: str = "PLATFORM_OPERATIONS",
        is_destructive: bool = False,
        cost_dollars: float = 0.0,
        data_classification: str = "INTERNAL",
    ) -> AgentRiskAssessment:
        dim_scores = {}

        # 1. Action reversibility
        if is_destructive or "DELETE" in proposed_action.upper():
            dim_scores[AgentRiskDimension.ACTION_REVERSIBILITY.value] = 0.95
        else:
            dim_scores[AgentRiskDimension.ACTION_REVERSIBILITY.value] = 0.1

        # 2. Data sensitivity
        if data_classification in ("RESTRICTED", "CONFIDENTIAL"):
            dim_scores[AgentRiskDimension.DATA_SENSITIVITY.value] = 0.7
        else:
            dim_scores[AgentRiskDimension.DATA_SENSITIVITY.value] = 0.2

        # 3. Financial impact
        if cost_dollars > 1000.0:
            dim_scores[AgentRiskDimension.FINANCIAL_IMPACT.value] = 0.8
        else:
            dim_scores[AgentRiskDimension.FINANCIAL_IMPACT.value] = 0.15

        # Calculate composite score
        composite = max(dim_scores.values()) if dim_scores else 0.2
        if composite >= 0.8:
            level = "CRITICAL" if is_destructive else "HIGH"
            requires_app = True
        elif composite >= 0.5:
            level = "MEDIUM"
            requires_app = False
        else:
            level = "LOW"
            requires_app = False

        mitigations = []
        if requires_app:
            mitigations.append("Require mandatory human approval before proceeding.")
        mitigations.append("Log immutable execution trace and enforce runtime safeguard timeouts.")

        assessment = AgentRiskAssessment(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task_id,
            composite_score=composite,
            level=level,
            requires_approval=requires_app,
            dimension_scores=dim_scores,
            mitigations=mitigations,
        )
        self._assessments[assessment.risk_id] = assessment
        return assessment

    def get_risk_assessment(self, risk_id: str, tenant_id: str) -> AgentRiskAssessment:
        ass = self._assessments.get(risk_id)
        if not ass:
            return AgentRiskAssessment(risk_id=risk_id, tenant_id=tenant_id, agent_id="unknown", task_id="unknown")
            
        try:
            self.tenant_guard.enforce_isolation(tenant_id, ass.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, ass.tenant_id)

        return ass
