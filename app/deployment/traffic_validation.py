from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import TrafficValidationStatus
from app.deployment.secrets import SecretsSanitizer


@dataclass
class TrafficThresholds:
    max_error_rate: float = 0.01  # Max 1% error rate
    max_p95_latency_ms: float = 500.0  # Max 500ms p95 latency
    min_success_rate: float = 0.99  # Min 99% success rate
    required_probes_healthy: bool = True
    require_matching_artifact_digest: bool = True


@dataclass
class TrafficValidationResult:
    status: TrafficValidationStatus
    valid: bool
    traffic_percentage: int
    error_rate: float
    p95_latency_ms: float
    success_rate: float
    probes_healthy: bool
    artifact_digest_matching: bool
    blocking_reasons: List[str] = field(default_factory=list)
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "status": self.status.value,
            "valid": self.valid,
            "traffic_percentage": self.traffic_percentage,
            "error_rate": self.error_rate,
            "p95_latency_ms": self.p95_latency_ms,
            "success_rate": self.success_rate,
            "probes_healthy": self.probes_healthy,
            "artifact_digest_matching": self.artifact_digest_matching,
            "blocking_reasons": self.blocking_reasons,
            "evaluated_at": self.evaluated_at,
        })


class TrafficValidationEngine:
    """Validates real-time request metrics, error rates, latency SLAs, probe contracts, and digest consistency."""

    @classmethod
    def validate_traffic(
        cls,
        traffic_percentage: int,
        runtime_metrics: Dict[str, Any],
        expected_artifact_digest: Optional[str] = None,
        runtime_artifact_digest: Optional[str] = None,
        thresholds: Optional[TrafficThresholds] = None,
    ) -> TrafficValidationResult:
        thresh = thresholds or TrafficThresholds()
        blocking_reasons: List[str] = []

        error_rate = float(runtime_metrics.get("error_rate", 0.0))
        p95_latency = float(runtime_metrics.get("p95_latency_ms", 0.0))
        success_rate = float(runtime_metrics.get("success_rate", 1.0 - error_rate))
        probes_healthy = bool(runtime_metrics.get("probes_healthy", True))

        # 1. Error Rate Guard
        if error_rate > thresh.max_error_rate:
            blocking_reasons.append(f"TRAFFIC_VALIDATION_FAILED: Error rate {error_rate:.4f} exceeded threshold {thresh.max_error_rate:.4f}")

        # 2. Latency SLA Guard
        if p95_latency > thresh.max_p95_latency_ms:
            blocking_reasons.append(f"TRAFFIC_VALIDATION_FAILED: p95 latency {p95_latency:.2f}ms exceeded SLA threshold {thresh.max_p95_latency_ms:.2f}ms")

        # 3. Success Rate Guard
        if success_rate < thresh.min_success_rate:
            blocking_reasons.append(f"TRAFFIC_VALIDATION_FAILED: Success rate {success_rate:.4f} below minimum threshold {thresh.min_success_rate:.4f}")

        # 4. Probe Health Guard
        if thresh.required_probes_healthy and not probes_healthy:
            blocking_reasons.append("TRAFFIC_VALIDATION_FAILED: Runtime health probes failed during traffic validation")

        # 5. Digest Consistency Guard
        digest_match = True
        if thresh.require_matching_artifact_digest and expected_artifact_digest and runtime_artifact_digest:
            if expected_artifact_digest != runtime_artifact_digest:
                digest_match = False
                blocking_reasons.append(f"DEPLOYMENT_ARTIFACT_MISMATCH: Runtime artifact digest '{runtime_artifact_digest}' != expected digest '{expected_artifact_digest}'")

        is_valid = len(blocking_reasons) == 0
        status = TrafficValidationStatus.PASSED if is_valid else TrafficValidationStatus.FAILED

        return TrafficValidationResult(
            status=status,
            valid=is_valid,
            traffic_percentage=traffic_percentage,
            error_rate=error_rate,
            p95_latency_ms=p95_latency,
            success_rate=success_rate,
            probes_healthy=probes_healthy,
            artifact_digest_matching=digest_match,
            blocking_reasons=blocking_reasons,
        )
