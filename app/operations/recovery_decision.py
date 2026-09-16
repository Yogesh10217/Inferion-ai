"""
Recovery Decision Engine Module for Phase 5.68.
Generates advisory recovery recommendations without automatically executing production infrastructure actions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.alerting import Alert
from app.operations.error_budget import ErrorBudgetResult, ErrorBudgetStatus
from app.operations.incident_management import Incident, IncidentSeverity
from app.operations.slo import SLOResult


class RecoveryRecommendation(str, Enum):
    NO_ACTION = "NO_ACTION"
    CONTINUE_MONITORING = "CONTINUE_MONITORING"
    MANUAL_INVESTIGATION_REQUIRED = "MANUAL_INVESTIGATION_REQUIRED"
    RESTART_RECOMMENDED = "RESTART_RECOMMENDED"
    ROLLBACK_RECOMMENDED = "ROLLBACK_RECOMMENDED"
    TRAFFIC_SHIFT_RECOMMENDED = "TRAFFIC_SHIFT_RECOMMENDED"
    EMERGENCY_INTERVENTION_REQUIRED = "EMERGENCY_INTERVENTION_REQUIRED"


@dataclass
class RecoveryDecision:
    recommendation: RecoveryRecommendation
    reasoning: str
    auto_execution_blocked: bool
    evidence_level: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation": self.recommendation.value,
            "reasoning": SecretsSanitizer.sanitize_string(self.reasoning),
            "auto_execution_blocked": self.auto_execution_blocked,
            "evidence_level": self.evidence_level,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class RecoveryDecisionEngine:
    """Evaluates incident severity, SLO breaches, and error budgets to issue non-destructive recommendations."""

    def evaluate_recovery(
        self,
        incident: Optional[Incident],
        slo_results: List[SLOResult],
        error_budget_result: Optional[ErrorBudgetResult],
        alerts: List[Alert],
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> RecoveryDecision:
        # Strict Rule: auto_execution_blocked is ALWAYS True
        auto_execution_blocked = True

        if not incident and not alerts:
            return RecoveryDecision(
                recommendation=RecoveryRecommendation.NO_ACTION,
                reasoning="System operationally healthy. No recovery action recommended.",
                auto_execution_blocked=auto_execution_blocked,
                evidence_level=evidence_level,
                details={},
            )

        if incident and incident.severity == IncidentSeverity.P1:
            rec = RecoveryRecommendation.EMERGENCY_INTERVENTION_REQUIRED
            reason = "P1 Critical Platform Outage detected. Emergency operator intervention required."
        elif error_budget_result and error_budget_result.status == ErrorBudgetStatus.EXHAUSTED:
            rec = RecoveryRecommendation.ROLLBACK_RECOMMENDED
            reason = "Error budget exhausted. Rollback to prior stable release is recommended for operator approval."
        elif any(a.alert_type == "DEPLOYMENT_REGRESSION" for a in alerts):
            rec = RecoveryRecommendation.ROLLBACK_RECOMMENDED
            reason = "Deployment regression detected. Rollback recommended."
        elif any(a.alert_type == "PROBE_FAILURE" for a in alerts):
            rec = RecoveryRecommendation.RESTART_RECOMMENDED
            reason = "Health probe failure detected. Service restart recommended."
        elif any(a.alert_type == "TRAFFIC_ANOMALY" for a in alerts):
            rec = RecoveryRecommendation.TRAFFIC_SHIFT_RECOMMENDED
            reason = "Traffic anomaly detected. Traffic shift to fallback pool recommended."
        elif incident and incident.severity in (IncidentSeverity.P2, IncidentSeverity.P3):
            rec = RecoveryRecommendation.MANUAL_INVESTIGATION_REQUIRED
            reason = f"Incident {incident.incident_id} ({incident.severity.value}) active. Manual investigation required."
        else:
            rec = RecoveryRecommendation.CONTINUE_MONITORING
            reason = "Minor operational alerts present. Continue monitoring telemetry."

        return RecoveryDecision(
            recommendation=rec,
            reasoning=reason,
            auto_execution_blocked=auto_execution_blocked,
            evidence_level=evidence_level,
            details={
                "incident": incident.to_dict() if incident else None,
                "alerts_count": len(alerts),
            },
        )
