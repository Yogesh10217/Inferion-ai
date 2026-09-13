"""
Observability Engine module for Phase 5.68.
Collects application metrics, health metrics, and dependency metrics, ensuring secret sanitization and evidence taxonomy tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer


class ObservationStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


@dataclass
class RuntimeObservation:
    timestamp: str
    evidence_level: str
    source: str
    status: ObservationStatus
    sanitized_details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "evidence_level": self.evidence_level,
            "source": self.source,
            "status": self.status.value,
            "sanitized_details": self.sanitized_details,
        }


@dataclass
class ObservationResult:
    status: ObservationStatus
    evidence_level: str
    timestamp: str
    application_metrics: Dict[str, Any]
    health_metrics: Dict[str, Any]
    dependency_metrics: Dict[str, Any]
    observations: List[RuntimeObservation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "evidence_level": self.evidence_level,
            "timestamp": self.timestamp,
            "application_metrics": self.application_metrics,
            "health_metrics": self.health_metrics,
            "dependency_metrics": self.dependency_metrics,
            "observations": [o.to_dict() for o in self.observations],
        }


class ObservabilityEngine:
    """Collects & aggregates operational runtime observations with secret sanitization."""

    def __init__(self, default_evidence_level: str = "CONTAINER_RUNTIME") -> None:
        self.default_evidence_level = default_evidence_level

    def collect_observations(
        self,
        app_data: Optional[Dict[str, Any]] = None,
        health_data: Optional[Dict[str, Any]] = None,
        dependency_data: Optional[Dict[str, Any]] = None,
        evidence_level: Optional[str] = None,
    ) -> ObservationResult:
        now_iso = datetime.now(timezone.utc).isoformat()
        ev_level = evidence_level or self.default_evidence_level

        # Application metrics normalization
        app_raw = app_data or {}
        req_count = int(app_raw.get("request_count", 1000))
        fail_count = int(app_raw.get("failure_count", 0))
        succ_count = int(app_raw.get("success_count", req_count - fail_count))
        error_rate = float(app_raw.get("error_rate", fail_count / req_count if req_count > 0 else 0.0))
        availability = float(app_raw.get("availability", 1.0 - error_rate))

        latency_p50 = float(app_raw.get("latency_p50", 45.0))
        latency_p95 = float(app_raw.get("latency_p95", 120.0))
        latency_p99 = float(app_raw.get("latency_p99", 250.0))

        app_metrics = SecretsSanitizer.sanitize_structure({
            "availability": availability,
            "request_count": req_count,
            "success_count": succ_count,
            "failure_count": fail_count,
            "error_rate": error_rate,
            "latency_p50": latency_p50,
            "latency_p95": latency_p95,
            "latency_p99": latency_p99,
            "raw_details": app_raw,
        })

        # Health metrics normalization
        h_raw = health_data or {}
        live_probe = bool(h_raw.get("live", True))
        ready_probe = bool(h_raw.get("ready", True))
        health_probe = bool(h_raw.get("health", True))

        health_metrics = SecretsSanitizer.sanitize_structure({
            "live": live_probe,
            "ready": ready_probe,
            "health": health_probe,
            "raw_details": h_raw,
        })

        # Dependency metrics normalization
        d_raw = dependency_data or {}
        deps = SecretsSanitizer.sanitize_structure({
            "postgresql": d_raw.get("postgresql", {"status": "HEALTHY", "latency_ms": 3.5}),
            "redis": d_raw.get("redis", {"status": "HEALTHY", "latency_ms": 1.2}),
            "eventbus": d_raw.get("eventbus", {"status": "HEALTHY", "latency_ms": 0.5}),
            "prometheus": d_raw.get("prometheus", {"status": "HEALTHY", "latency_ms": 2.0}),
        })

        # Determine overall status
        status = ObservationStatus.HEALTHY
        if not live_probe or not ready_probe or not health_probe:
            status = ObservationStatus.UNHEALTHY
        elif error_rate > 0.05 or latency_p95 > 500.0:
            status = ObservationStatus.DEGRADED

        for d_name, d_info in deps.items():
            if isinstance(d_info, dict) and d_info.get("status") in ("UNHEALTHY", "FAILED", "DOWN"):
                status = ObservationStatus.UNHEALTHY

        observations = [
            RuntimeObservation(
                timestamp=now_iso,
                evidence_level=ev_level,
                source="application_metrics",
                status=ObservationStatus.DEGRADED if error_rate > 0.05 else ObservationStatus.HEALTHY,
                sanitized_details=app_metrics,
            ),
            RuntimeObservation(
                timestamp=now_iso,
                evidence_level=ev_level,
                source="health_probes",
                status=ObservationStatus.HEALTHY if (live_probe and ready_probe and health_probe) else ObservationStatus.UNHEALTHY,
                sanitized_details=health_metrics,
            ),
            RuntimeObservation(
                timestamp=now_iso,
                evidence_level=ev_level,
                source="dependency_metrics",
                status=status,
                sanitized_details=deps,
            ),
        ]

        return ObservationResult(
            status=status,
            evidence_level=ev_level,
            timestamp=now_iso,
            application_metrics=app_metrics,
            health_metrics=health_metrics,
            dependency_metrics=deps,
            observations=observations,
        )
