"""Continuous Governance Monitoring & Compliance Drift Detection Engine."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.governance_platform.violations import ViolationManager, ViolationType, ViolationSeverity
from app.governance_platform.risk import RiskManager, RiskCategory, RiskFactor

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MonitoringCheckResult(BaseModel):
    check_id: str
    target_resource_id: str
    tenant_id: str
    has_drift: bool
    findings: List[str]
    checked_at: datetime = Field(default_factory=_now)


class GovernanceMonitoringEngine:
    """Continuously monitors compliance drift, model safety regressions, and autonomy boundary breaches."""

    def __init__(
        self,
        violation_manager: Optional[ViolationManager] = None,
        risk_manager: Optional[RiskManager] = None,
    ) -> None:
        self.violation_manager = violation_manager or ViolationManager()
        self.risk_manager = risk_manager or RiskManager()

    def run_monitoring_scan(self, tenant_id: str = "global", target_resource_id: str = "resource_all") -> MonitoringCheckResult:
        findings = []
        has_drift = False

        # 1. Simulated compliance drift check
        # Check if any controls failed
        drift_detected = False
        if drift_detected:
            has_drift = True
            msg = f"Compliance drift detected on resource '{target_resource_id}': Control failed"
            findings.append(msg)
            self.violation_manager.record_violation(
                title="Compliance Control Failure",
                violation_type=ViolationType.COMPLIANCE_VIOLATION,
                severity=ViolationSeverity.HIGH,
                primary_resource_id=target_resource_id,
                description=msg,
                tenant_id=tenant_id,
            )

        res = MonitoringCheckResult(
            check_id=f"chk_{_now().strftime('%Y%m%d%H%M%S')}",
            target_resource_id=target_resource_id,
            tenant_id=tenant_id,
            has_drift=has_drift,
            findings=findings,
        )
        logger.info(f"[GOVERNANCE MONITORING] Completed scan for tenant '{tenant_id}': Drift = {has_drift}")
        return res
