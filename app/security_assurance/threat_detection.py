"""Threat Detector & Detection Rules Engine."""

import logging
from typing import List, Optional

from app.security_assurance.threat_indicators import ThreatIndicatorManager
from app.security_assurance.threats import SecurityThreat, SecurityThreatStore, ThreatSeverity, ThreatType

logger = logging.getLogger(__name__)


class SecurityThreatDetector:
    """Detects security threats from inputs, signals, and threat indicators."""

    def __init__(self, threat_store: SecurityThreatStore, indicator_manager: ThreatIndicatorManager) -> None:
        self.threat_store = threat_store
        self.indicator_manager = indicator_manager

    def scan_input(
        self,
        tenant_id: str,
        input_text: str,
        asset_id: Optional[str] = None,
    ) -> List[SecurityThreat]:
        detected_threats: List[SecurityThreat] = []
        matches = self.indicator_manager.match_payload(tenant_id, input_text)

        lowered = input_text.lower()
        if matches:
            is_injection = any(k in lowered for k in ["ignore", "override", "bypass", "system prompt", "instruction"])
            threat = self.threat_store.record_threat(
                tenant_id=tenant_id,
                title=f"Indicator match detected in payload for asset {asset_id or 'unknown'}",
                threat_type=ThreatType.PROMPT_INJECTION if is_injection else ThreatType.ANOMALOUS_API_TRAFFIC,
                severity=ThreatSeverity.CRITICAL if is_injection else ThreatSeverity.HIGH,
                target_asset_id=asset_id,
                description=f"Payload matched {len(matches)} threat indicators.",
                indicators=[m.value for m in matches],
            )
            detected_threats.append(threat)

        # Basic heuristic injection check
        lowered = input_text.lower()
        if "ignore all previous instructions" in lowered or "system prompt override" in lowered:
            threat = self.threat_store.record_threat(
                tenant_id=tenant_id,
                title="Prompt Injection Attack Detected",
                threat_type=ThreatType.PROMPT_INJECTION,
                severity=ThreatSeverity.CRITICAL,
                target_asset_id=asset_id,
                description="Input contained direct system prompt override attempt.",
                indicators=["ignore all previous instructions"],
            )
            detected_threats.append(threat)

        return detected_threats
