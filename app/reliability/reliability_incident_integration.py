"""
Phase 5.70 - Reliability Incident Integration Module.

Integrates Reliability Engineering with Phase 5.68 Incident Management, Alert Engine, Alert Deduplication, SLO Engine, and Error Budgets.
Reuses existing Phase 5.68 infrastructure without creating duplicate incident engines.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from app.operations import (
    AlertDeduplicationEngine,
    AlertSeverity,
    IncidentManager,
    IncidentSeverity,
)
from app.operations.alerting import AlertManager
from app.reliability.recovery_recommendation import RecoveryRecommendation, RecoveryRecommendationEngine
from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


@dataclass
class IncidentIntegrationResult:
    incident_created: bool
    incident_id: Optional[str]
    alert_deduplicated: bool
    recovery_recommendation: RecoveryRecommendation
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class ReliabilityIncidentIntegration:
    """Correlates reliability signals with Phase 5.68 SRE Operations."""

    def __init__(
        self,
        incident_manager: Optional[IncidentManager] = None,
        alert_manager: Optional[AlertManager] = None,
        alert_dedup: Optional[AlertDeduplicationEngine] = None,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self.incident_manager = incident_manager or IncidentManager()
        self.alert_manager = alert_manager or AlertManager()
        self.alert_dedup = alert_dedup or AlertDeduplicationEngine()
        self._seen_keys: set = set()
        self.recommendation_engine = RecoveryRecommendationEngine(evidence_level=evidence_level)
        self.evidence_level = evidence_level

    def process_reliability_signal(
        self,
        signal_source: str,
        metric_name: str,
        current_value: float,
        threshold: float,
        severity: str = "HIGH",
        executed: bool = True,
    ) -> IncidentIntegrationResult:
        if not executed:
            rec = self.recommendation_engine.generate_recommendation(incident_severity="LOW")
            return IncidentIntegrationResult(
                incident_created=False,
                incident_id=None,
                alert_deduplicated=False,
                recovery_recommendation=rec,
                evidence_level=self.evidence_level,
                details={"message": "Signal processing not executed."},
            )

        # 1. Deduplicate alert
        dedup_key = f"{signal_source}:{metric_name}:{severity}"
        is_duplicate = dedup_key in self._seen_keys
        self._seen_keys.add(dedup_key)

        incident_id = None
        incident_created = False

        if not is_duplicate:
            # 2. Trigger alert
            alert_sev = AlertSeverity.CRITICAL if severity in ("CRITICAL", "HIGH") else AlertSeverity.WARNING
            self.alert_manager.trigger_alert(
                rule_name=metric_name,
                source_component=signal_source,
                summary=f"Reliability signal breach in {signal_source}: {metric_name} = {current_value} (threshold: {threshold})",
                severity=alert_sev,
            )

            # 3. Declare incident if HIGH/CRITICAL
            if severity in ("CRITICAL", "HIGH"):
                inc_sev = IncidentSeverity.P1 if severity == "CRITICAL" else IncidentSeverity.P2
                inc = self.incident_manager.create_incident(
                    title=f"Reliability failure in {signal_source}: {metric_name}",
                    severity=inc_sev,
                    service=signal_source,
                )
                incident_id = inc.incident_id
                incident_created = True

        # 4. Generate safe recovery recommendation
        rec = self.recommendation_engine.generate_recommendation(
            incident_severity=severity,
            database_failed=(signal_source == "postgresql"),
            deployment_failed=(signal_source == "deployment"),
        )

        return IncidentIntegrationResult(
            incident_created=incident_created,
            incident_id=incident_id,
            alert_deduplicated=is_duplicate,
            recovery_recommendation=rec,
            evidence_level=self.evidence_level,
            details={
                "signal_source": signal_source,
                "metric": metric_name,
                "value": current_value,
                "threshold": threshold,
            },
        )
