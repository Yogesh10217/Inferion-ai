"""Control effectiveness engine for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Any, Dict, Optional

from app.continuous_assurance.models import (
    ControlEffectivenessAssessment,
    ControlEffectivenessStatus,
)
from app.continuous_assurance.repositories import ControlEffectivenessRepository

logger = logging.getLogger(__name__)


class ControlEffectivenessEngine:
    """Evaluates control effectiveness across enterprise domains without mutating infrastructure."""

    def __init__(self, ctrl_repo: ControlEffectivenessRepository) -> None:
        self.ctrl_repo = ctrl_repo

    def evaluate_control(
        self, tenant_id: str, control_id: str, evidence_data: Optional[Dict[str, Any]] = None
    ) -> ControlEffectivenessAssessment:
        evidence = evidence_data or {}
        pass_rate = evidence.get("pass_rate", 0.95)

        if pass_rate >= 0.90:
            status = ControlEffectivenessStatus.EFFECTIVE
        elif pass_rate >= 0.70:
            status = ControlEffectivenessStatus.PARTIALLY_EFFECTIVE
        elif pass_rate >= 0.50:
            status = ControlEffectivenessStatus.DEGRADED
        else:
            status = ControlEffectivenessStatus.INEFFECTIVE

        assessment = ControlEffectivenessAssessment(
            tenant_id=tenant_id,
            control_id=control_id,
            status=status,
            score=round(pass_rate, 4),
            evidence_references=[f"ev_ref_{control_id}_01"],
        )

        self.ctrl_repo.save(assessment)
        logger.info(f"Evaluated control '{control_id}' for tenant '{tenant_id}' -> Status: {status.value}")
        return assessment
