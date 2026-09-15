"""
Security Threat Classifier Module for Phase 5.69.
Classifies security threats and issues non-auto-executing recommendations (auto_execution_blocked = True).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict

from app.deployment.secrets import SecretsSanitizer


class ThreatSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"
    EMERGENCY = "EMERGENCY"


class ThreatDecision(str, Enum):
    MONITOR = "MONITOR"
    INVESTIGATE = "INVESTIGATE"
    ESCALATE = "ESCALATE"
    BLOCK_RELEASE = "BLOCK_RELEASE"
    ROLLBACK_RECOMMENDED = "ROLLBACK_RECOMMENDED"


@dataclass
class SecurityThreat:
    threat_id: str
    severity: Any
    decision: Any
    summary: str
    auto_execution_blocked: bool = True
    fingerprint: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.fingerprint:
            sev_str = self.severity.value if isinstance(self.severity, Enum) else str(self.severity)
            dec_str = self.decision.value if isinstance(self.decision, Enum) else str(self.decision)
            payload = {
                "id": self.threat_id,
                "severity": sev_str,
                "decision": dec_str,
            }
            self.fingerprint = f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"

    def to_dict(self) -> Dict[str, Any]:
        sev_str = self.severity.value if isinstance(self.severity, Enum) else str(self.severity)
        dec_str = self.decision.value if isinstance(self.decision, Enum) else str(self.decision)
        return {
            "threat_id": self.threat_id,
            "severity": sev_str,
            "decision": dec_str,
            "summary": SecretsSanitizer.sanitize_string(self.summary),
            "auto_execution_blocked": self.auto_execution_blocked,
            "fingerprint": self.fingerprint,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SecurityThreatClassifier:
    """Classifies threat telemetry and emits advisory decisions."""

    def classify_threat(
        self,
        threat_type: str = "SECURITY_POLICY_VIOLATION",
        severity: Any = ThreatSeverity.HIGH,
        description: str = "",
        summary: str = "",
        affected_component: str = "",
    ) -> SecurityThreat:
        if isinstance(severity, str):
            try:
                sev_enum = ThreatSeverity(severity.upper())
            except ValueError:
                sev_enum = ThreatSeverity.HIGH
        else:
            sev_enum = severity

        if sev_enum in (ThreatSeverity.EMERGENCY, ThreatSeverity.CRITICAL):
            decision = ThreatDecision.BLOCK_RELEASE.value if threat_type != "ARTIFACT_TAMPERING" else ThreatDecision.ROLLBACK_RECOMMENDED.value
        elif sev_enum == ThreatSeverity.HIGH:
            decision = ThreatDecision.ESCALATE.value
        elif sev_enum == ThreatSeverity.MEDIUM:
            decision = ThreatDecision.INVESTIGATE.value
        else:
            decision = ThreatDecision.MONITOR.value

        threat_summary = summary or description or f"Threat detected: {threat_type}"

        return SecurityThreat(
            threat_id=f"threat-{threat_type.lower()}",
            severity=sev_enum.value if isinstance(sev_enum, Enum) else str(sev_enum),
            decision=decision,
            summary=threat_summary,
            auto_execution_blocked=True,
            details={"threat_type": threat_type, "affected_component": affected_component},
        )
