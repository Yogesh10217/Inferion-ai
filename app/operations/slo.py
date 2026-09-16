"""
Service Level Objective (SLO) System for Phase 5.68 and legacy operations support.
Evaluates SLI results against defined SLO targets and warning thresholds.
"""

from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.deployment.secrets import SecretsSanitizer
from app.observability.sla import SLAEngine as BaseSLAEngine
from app.operations.sli import SLIResult, SLIType

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class SLOType(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    LATENCY = "LATENCY"
    ERROR_RATE = "ERROR_RATE"
    THROUGHPUT = "THROUGHPUT"
    QUEUE_DELAY = "QUEUE_DELAY"
    MODEL_LATENCY = "MODEL_LATENCY"
    TOKEN_LATENCY = "TOKEN_LATENCY"
    TOOL_SUCCESS_RATE = "TOOL_SUCCESS_RATE"
    WORKFLOW_SUCCESS_RATE = "WORKFLOW_SUCCESS_RATE"
    DATA_FRESHNESS = "DATA_FRESHNESS"
    QUALITY_SCORE = "QUALITY_SCORE"
    CUSTOM = "CUSTOM"


class SLOStatus(str, Enum):
    MET = "MET"
    AT_RISK = "AT_RISK"
    BREACHED = "BREACHED"
    NOT_ENOUGH_DATA = "NOT_ENOUGH_DATA"
    NOT_EXECUTED = "NOT_EXECUTED"
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"


# Legacy / General SLO Pydantic Model
class LegacyServiceLevelObjective(BaseModel):
    slo_id: str = Field(default_factory=lambda: f"slo_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    slo_type: SLOType = SLOType.AVAILABILITY
    target_percentage: float = 99.9

    current_value: float = 100.0
    error_budget_remaining_percent: float = 100.0
    burn_rate: float = 0.0
    status: SLOStatus = SLOStatus.HEALTHY

    window_days: int = 30
    created_at: datetime = Field(default_factory=_now)


# Phase 5.68 Dataclass SLO Model
@dataclass
class ServiceLevelObjective:
    name: str
    sli_type: SLIType
    target_value: float
    warning_threshold: float
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "sli_type": self.sli_type.value if hasattr(self.sli_type, "value") else str(self.sli_type),
            "target_value": self.target_value,
            "warning_threshold": self.warning_threshold,
            "description": self.description,
        }


@dataclass
class SLOResult:
    slo: ServiceLevelObjective
    status: SLOStatus
    observed_value: float
    target_value: float
    warning_threshold: float
    failure_reason: Optional[str]
    evidence_level: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "slo": self.slo.to_dict(),
            "status": self.status.value,
            "observed_value": self.observed_value,
            "target_value": self.target_value,
            "warning_threshold": self.warning_threshold,
            "failure_reason": self.failure_reason,
            "evidence_level": self.evidence_level,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SLOEvaluator:
    """Evaluates SLI results into SLO statuses deterministically."""

    def __init__(self, default_slos: Optional[List[ServiceLevelObjective]] = None) -> None:
        self.slos = default_slos or [
            ServiceLevelObjective("Availability SLO", SLIType.AVAILABILITY, target_value=0.999, warning_threshold=0.9995, description="99.9% availability"),
            ServiceLevelObjective("Error Rate SLO", SLIType.ERROR_RATE, target_value=0.01, warning_threshold=0.005, description="Error rate <= 1%"),
            ServiceLevelObjective("p95 Latency SLO", SLIType.LATENCY_P95, target_value=500.0, warning_threshold=400.0, description="p95 latency <= 500ms"),
            ServiceLevelObjective("Health Probes SLO", SLIType.HEALTH_PROBE, target_value=1.0, warning_threshold=1.0, description="100% healthy probes"),
            ServiceLevelObjective("Dependency SLO", SLIType.DEPENDENCY_AVAILABILITY, target_value=1.0, warning_threshold=1.0, description="100% dependency availability"),
        ]

    def evaluate(self, sli_results: List[SLIResult]) -> List[SLOResult]:
        sli_map = {res.sli_type: res for res in sli_results}
        results = []

        for slo in self.slos:
            sli_res = sli_map.get(slo.sli_type)
            if not sli_res:
                results.append(
                    SLOResult(
                        slo=slo,
                        status=SLOStatus.NOT_ENOUGH_DATA,
                        observed_value=0.0,
                        target_value=slo.target_value,
                        warning_threshold=slo.warning_threshold,
                        failure_reason="No matching SLI data collected",
                        evidence_level="NOT_EXECUTED",
                        details={},
                    )
                )
                continue

            obs = sli_res.observed_value
            ev_level = sli_res.evidence_level
            status = SLOStatus.MET
            reason = None

            if slo.sli_type in (SLIType.AVAILABILITY, SLIType.LIVE_PROBE, SLIType.READY_PROBE, SLIType.HEALTH_PROBE, SLIType.DEPENDENCY_AVAILABILITY):
                if obs < slo.target_value:
                    status = SLOStatus.BREACHED
                    reason = f"Observed value {obs} fell below SLO target {slo.target_value}"
                elif obs < slo.warning_threshold:
                    status = SLOStatus.AT_RISK
                    reason = f"Observed value {obs} fell below warning threshold {slo.warning_threshold}"
            elif slo.sli_type in (SLIType.ERROR_RATE, SLIType.LATENCY_P50, SLIType.LATENCY_P95, SLIType.LATENCY_P99):
                if obs > slo.target_value:
                    status = SLOStatus.BREACHED
                    reason = f"Observed value {obs} exceeded SLO target {slo.target_value}"
                elif obs > slo.warning_threshold:
                    status = SLOStatus.AT_RISK
                    reason = f"Observed value {obs} exceeded warning threshold {slo.warning_threshold}"

            results.append(
                SLOResult(
                    slo=slo,
                    status=status,
                    observed_value=obs,
                    target_value=slo.target_value,
                    warning_threshold=slo.warning_threshold,
                    failure_reason=reason,
                    evidence_level=ev_level,
                    details={"sli_result": sli_res.to_dict()},
                )
            )

        return results


class SLOManager:
    """Evaluates Service Level Objectives, error budgets, and burn-rates per tenant."""

    def __init__(self, base_sla_engine: Optional[BaseSLAEngine] = None) -> None:
        self.base_sla_engine = base_sla_engine or BaseSLAEngine()
        self._slos: Dict[str, LegacyServiceLevelObjective] = {}

    def create_slo(
        self,
        name: str,
        target_percentage: float,
        tenant_id: str = "global",
        slo_type: SLOType = SLOType.AVAILABILITY,
        window_days: int = 30,
    ) -> LegacyServiceLevelObjective:
        slo = LegacyServiceLevelObjective(
            name=name,
            target_percentage=target_percentage,
            tenant_id=tenant_id,
            slo_type=slo_type,
            window_days=window_days,
        )
        self._slos[slo.slo_id] = slo
        logger.info(f"[SLO MANAGER] Created SLO '{name}' (Target: {target_percentage}%, Tenant: '{tenant_id}')")
        return slo

    def record_measurement(self, slo_id: str, current_value: float) -> LegacyServiceLevelObjective:
        slo = self.get_slo(slo_id)
        slo.current_value = current_value

        allowed_error = 100.0 - slo.target_percentage
        actual_error = max(0.0, 100.0 - current_value)

        if current_value >= slo.target_percentage:
            remaining_eb = 100.0
            burn = 0.0
        else:
            remaining_eb = max(0.0, 100.0 - (actual_error / allowed_error * 100.0)) if allowed_error > 0.0 else 0.0
            burn = float(actual_error / allowed_error) if allowed_error > 0.0 else 1.0

        slo.error_budget_remaining_percent = float(remaining_eb)
        slo.burn_rate = burn

        if current_value < slo.target_percentage:
            slo.status = SLOStatus.BREACHED
        elif remaining_eb <= 20.0:
            slo.status = SLOStatus.WARNING
        else:
            slo.status = SLOStatus.HEALTHY

        logger.info(f"[SLO MANAGER] Measured SLO '{slo.name}': Current = {current_value}%, Error Budget = {remaining_eb:.1f}%, Status = {slo.status.value}")
        return slo

    def get_slo(self, slo_id: str) -> LegacyServiceLevelObjective:
        slo = self._slos.get(slo_id)
        if not slo:
            raise KeyError(f"SLO '{slo_id}' not found")
        return slo

    def list_slos(self, tenant_id: Optional[str] = None) -> List[LegacyServiceLevelObjective]:
        res = list(self._slos.values())
        if tenant_id:
            res = [s for s in res if s.tenant_id == tenant_id]
        return res
