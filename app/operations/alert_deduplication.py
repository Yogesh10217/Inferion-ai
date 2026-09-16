"""
Alert Deduplication Engine Module for Phase 5.68.
Aggregates duplicate alerts using deterministic SHA-256 fingerprints into canonical alerts.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List

from app.deployment.secrets import SecretsSanitizer
from app.operations.alerting import Alert


@dataclass
class AlertFingerprint:
    alert_type: str
    service: str
    severity: str
    deployment_identity: str
    normalized_summary: str

    def compute_sha256(self) -> str:
        # Volatile timestamps are explicitly excluded from the fingerprint
        raw = f"{self.alert_type}|{self.service}|{self.severity}|{self.deployment_identity}|{self.normalized_summary.strip().lower()}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class AlertDeduplicationEngine:
    """Deduplicates redundant alerts using SHA-256 fingerprinting."""

    def deduplicate(self, raw_alerts: List[Alert]) -> List[Alert]:
        if not raw_alerts:
            return []

        dedup_map: Dict[str, Alert] = {}

        for alert in raw_alerts:
            sanitized_summary = SecretsSanitizer.sanitize_string(alert.summary)
            fp_obj = AlertFingerprint(
                alert_type=alert.alert_type,
                service=alert.service,
                severity=alert.severity.value,
                deployment_identity=alert.deployment_identity,
                normalized_summary=sanitized_summary,
            )
            fp_hash = fp_obj.compute_sha256()

            if fp_hash in dedup_map:
                existing = dedup_map[fp_hash]
                existing.occurrence_count += alert.occurrence_count
                # Keep existing alert details aggregated if needed
            else:
                alert.fingerprint = fp_hash
                alert.summary = sanitized_summary
                alert.details = SecretsSanitizer.sanitize_structure(alert.details)
                dedup_map[fp_hash] = alert

        return list(dedup_map.values())
