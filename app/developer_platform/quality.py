"""Software Quality Gates & Policy Enforcement Subsystem."""

import logging
import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.developer_platform.exceptions import QualityGateViolationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class QualityGate(BaseModel):
    gate_id: str = Field(default_factory=lambda: f"qgate_{uuid.uuid4().hex[:10]}")
    name: str = "Standard Quality Gate"
    min_coverage_pct: float = 80.0

    max_critical_bugs: int = 0
    tenant_id: str = "global"
    created_at: datetime = Field(default_factory=_now)


class QualityManager:
    """Evaluates deterministic quality thresholds before software deployment."""

    def evaluate_quality(self, gate: QualityGate, coverage_pct: float, critical_bugs: int) -> bool:
        if coverage_pct < gate.min_coverage_pct:
            reason = f"Coverage {coverage_pct}% is below required threshold {gate.min_coverage_pct}%"
            logger.warning(f"[QUALITY MANAGER] Quality gate '{gate.gate_id}' FAILED: {reason}")
            raise QualityGateViolationException(gate.gate_id, reason)

        if critical_bugs > gate.max_critical_bugs:
            reason = f"Critical bugs count {critical_bugs} exceeds max allowed {gate.max_critical_bugs}"
            logger.warning(f"[QUALITY MANAGER] Quality gate '{gate.gate_id}' FAILED: {reason}")
            raise QualityGateViolationException(gate.gate_id, reason)

        logger.info(
            f"[QUALITY MANAGER] Quality gate '{gate.gate_id}' PASSED (coverage={coverage_pct}%, bugs={critical_bugs})"
        )
        return True
