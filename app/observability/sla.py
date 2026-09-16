"""SLA and SLO Management Subsystem."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from app.observability.exceptions import SLAValidationException

logger = logging.getLogger(__name__)


class SLOStatus(str, Enum):
    """SLO Evaluation Status Enum."""
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    VIOLATED = "VIOLATED"
    UNKNOWN = "UNKNOWN"


@dataclass
class SLODefinition:
    """Represents a Service Level Objective rule definition."""
    slo_id: str
    name: str
    target_component: str
    metric_name: str  # latency_p95, availability, error_rate, duration, success_rate
    comparator: str  # <=, >=, <, >
    target_value: float
    warning_threshold: Optional[float] = None
    window_seconds: int = 3600
    tenant_id: Optional[str] = None
    workspace_id: Optional[str] = None
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SLOEvaluation:
    """Result of an SLO evaluation check."""
    slo_id: str
    name: str
    target_component: str
    status: SLOStatus
    current_value: float
    target_value: float
    comparator: str
    is_violated: bool
    evaluated_at: float = field(default_factory=time.time)
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        return d


class SLAEngine:
    """Engine for defining, evaluating, and tracking Service Level Objectives (SLOs)."""

    def __init__(self) -> None:
        self._slos: Dict[str, SLODefinition] = {}
        self._evaluations: Dict[str, SLOEvaluation] = {}
        self._violations_history: List[Dict[str, Any]] = []

    def create_slo(
        self,
        slo_id: str,
        name: str,
        target_component: str,
        metric_name: str,
        comparator: str,
        target_value: float,
        warning_threshold: Optional[float] = None,
        window_seconds: int = 3600,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> SLODefinition:
        """Create and register a new Service Level Objective definition."""
        if comparator not in ["<=", ">=", "<", ">"]:
            raise SLAValidationException(f"Invalid comparator '{comparator}'. Allowed: <=, >=, <, >")

        slo = SLODefinition(
            slo_id=slo_id,
            name=name,
            target_component=target_component,
            metric_name=metric_name,
            comparator=comparator,
            target_value=target_value,
            warning_threshold=warning_threshold,
            window_seconds=window_seconds,
            tenant_id=tenant_id,
            workspace_id=workspace_id,
        )

        self._slos[slo_id] = slo
        return slo

    def evaluate_slo(self, slo_id: str, current_value: float) -> SLOEvaluation:
        """Evaluate current metric value against an SLO rule."""
        slo = self._slos.get(slo_id)
        if not slo:
            raise SLAValidationException(f"SLO with ID '{slo_id}' not found.")

        comp = slo.comparator
        target = slo.target_value
        warn = slo.warning_threshold

        is_violated = False
        status = SLOStatus.HEALTHY

        if comp == "<=":
            if current_value > target:
                is_violated = True
                status = SLOStatus.VIOLATED
            elif warn is not None and current_value >= warn:
                status = SLOStatus.WARNING
        elif comp == "<":
            if current_value >= target:
                is_violated = True
                status = SLOStatus.VIOLATED
            elif warn is not None and current_value >= warn:
                status = SLOStatus.WARNING
        elif comp == ">=":
            if current_value < target:
                is_violated = True
                status = SLOStatus.VIOLATED
            elif warn is not None and current_value <= warn:
                status = SLOStatus.WARNING
        elif comp == ">":
            if current_value <= target:
                is_violated = True
                status = SLOStatus.VIOLATED
            elif warn is not None and current_value <= warn:
                status = SLOStatus.WARNING

        msg = f"SLO '{slo.name}' status is {status.value}. Current: {current_value}, Target: {comp} {target}"

        eval_result = SLOEvaluation(
            slo_id=slo_id,
            name=slo.name,
            target_component=slo.target_component,
            status=status,
            current_value=current_value,
            target_value=target,
            comparator=comp,
            is_violated=is_violated,
            message=msg,
        )

        self._evaluations[slo_id] = eval_result

        if is_violated:
            self._violations_history.append(eval_result.to_dict())

        return eval_result

    def get_slo_status(self, slo_id: str) -> Dict[str, Any]:
        """Get evaluation status for an SLO."""
        if slo_id not in self._slos:
            raise SLAValidationException(f"SLO with ID '{slo_id}' not found.")

        evaluation = self._evaluations.get(slo_id)
        slo = self._slos[slo_id]

        if not evaluation:
            return {
                "slo": slo.to_dict(),
                "status": SLOStatus.UNKNOWN.value,
                "latest_evaluation": None,
            }

        return {
            "slo": slo.to_dict(),
            "status": evaluation.status.value,
            "latest_evaluation": evaluation.to_dict(),
        }

    def get_all_slo_statuses(
        self,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Retrieve all registered SLO statuses filtered by tenant or workspace."""
        results = []
        for slo_id, slo in self._slos.items():
            if tenant_id and slo.tenant_id and slo.tenant_id != tenant_id:
                continue
            if workspace_id and slo.workspace_id and slo.workspace_id != workspace_id:
                continue
            results.append(self.get_slo_status(slo_id))
        return results

    def detect_violation(self, slo_id: str, current_value: float) -> Optional[Dict[str, Any]]:
        """Check for violation and return violation record if broken."""
        eval_res = self.evaluate_slo(slo_id, current_value)
        if eval_res.is_violated:
            return eval_res.to_dict()
        return None
