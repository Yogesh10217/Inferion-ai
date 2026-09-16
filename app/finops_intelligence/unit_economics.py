"""Enterprise AI Unit Economics (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException


class UnitEconomicMetric(BaseModel):
    unit_type: str  # PER_REQUEST, PER_WORKFLOW, PER_AGENT_TASK, PER_MODEL_EXECUTION, PER_TRANSACTION
    cost_per_unit_usd: float
    total_units: float
    total_cost_usd: float


class UnitEconomicAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"unit_ec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_entity: str
    metrics: List[UnitEconomicMetric] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UnitEconomicManager:
    """Calculates enterprise AI unit economics metrics."""

    def __init__(self) -> None:
        self._assessments: Dict[str, UnitEconomicAssessment] = {}

    def calculate_unit_economics(
        self,
        tenant_id: str,
        target_entity: str,
        total_cost_usd: float,
        total_requests: float = 1000.0,
        total_agent_tasks: float = 100.0,
    ) -> UnitEconomicAssessment:
        req_cost = round(total_cost_usd / max(total_requests, 1.0), 6)
        task_cost = round(total_cost_usd / max(total_agent_tasks, 1.0), 4)

        metrics = [
            UnitEconomicMetric(unit_type="PER_REQUEST", cost_per_unit_usd=req_cost, total_units=total_requests, total_cost_usd=total_cost_usd),
            UnitEconomicMetric(unit_type="PER_AGENT_TASK", cost_per_unit_usd=task_cost, total_units=total_agent_tasks, total_cost_usd=total_cost_usd),
        ]
        asm = UnitEconomicAssessment(
            tenant_id=tenant_id,
            target_entity=target_entity,
            metrics=metrics,
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> UnitEconomicAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return asm
