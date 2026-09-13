"""
Service Level Indicator (SLI) System for Phase 5.68.
Evaluates metrics against quantitative SLI definitions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.observability_engine import ObservationResult


class SLIType(str, Enum):
    AVAILABILITY = "AVAILABILITY"
    ERROR_RATE = "ERROR_RATE"
    LATENCY_P50 = "LATENCY_P50"
    LATENCY_P95 = "LATENCY_P95"
    LATENCY_P99 = "LATENCY_P99"
    LIVE_PROBE = "LIVE_PROBE"
    READY_PROBE = "READY_PROBE"
    HEALTH_PROBE = "HEALTH_PROBE"
    DEPENDENCY_AVAILABILITY = "DEPENDENCY_AVAILABILITY"


@dataclass
class ServiceLevelIndicator:
    name: str
    sli_type: SLIType
    target_value: float
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "sli_type": self.sli_type.value,
            "target_value": self.target_value,
            "description": self.description,
        }


@dataclass
class SLIResult:
    sli_type: SLIType
    name: str
    observed_value: float
    target_value: float
    is_satisfactory: bool
    evidence_level: str
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sli_type": self.sli_type.value,
            "name": self.name,
            "observed_value": self.observed_value,
            "target_value": self.target_value,
            "is_satisfactory": self.is_satisfactory,
            "evidence_level": self.evidence_level,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SLIEvaluator:
    """Evaluates runtime metrics into standard SLI results."""

    def __init__(self, default_indicators: Optional[List[ServiceLevelIndicator]] = None) -> None:
        self.indicators = default_indicators or [
            ServiceLevelIndicator("Availability Indicator", SLIType.AVAILABILITY, target_value=0.999),
            ServiceLevelIndicator("Error Rate Indicator", SLIType.ERROR_RATE, target_value=0.01),
            ServiceLevelIndicator("p50 Latency Indicator", SLIType.LATENCY_P50, target_value=100.0),
            ServiceLevelIndicator("p95 Latency Indicator", SLIType.LATENCY_P95, target_value=500.0),
            ServiceLevelIndicator("p99 Latency Indicator", SLIType.LATENCY_P99, target_value=1000.0),
            ServiceLevelIndicator("Liveness Probe Indicator", SLIType.LIVE_PROBE, target_value=1.0),
            ServiceLevelIndicator("Readiness Probe Indicator", SLIType.READY_PROBE, target_value=1.0),
            ServiceLevelIndicator("Health Probe Indicator", SLIType.HEALTH_PROBE, target_value=1.0),
            ServiceLevelIndicator("Dependency Availability Indicator", SLIType.DEPENDENCY_AVAILABILITY, target_value=1.0),
        ]

    def evaluate(self, observation: ObservationResult) -> List[SLIResult]:
        app_m = observation.application_metrics
        health_m = observation.health_metrics
        dep_m = observation.dependency_metrics
        ev_level = observation.evidence_level

        results = []
        for ind in self.indicators:
            observed = 0.0
            satisfactory = True

            if ind.sli_type == SLIType.AVAILABILITY:
                observed = float(app_m.get("availability", 1.0))
                satisfactory = observed >= ind.target_value
            elif ind.sli_type == SLIType.ERROR_RATE:
                observed = float(app_m.get("error_rate", 0.0))
                satisfactory = observed <= ind.target_value
            elif ind.sli_type == SLIType.LATENCY_P50:
                observed = float(app_m.get("latency_p50", 0.0))
                satisfactory = observed <= ind.target_value
            elif ind.sli_type == SLIType.LATENCY_P95:
                observed = float(app_m.get("latency_p95", 0.0))
                satisfactory = observed <= ind.target_value
            elif ind.sli_type == SLIType.LATENCY_P99:
                observed = float(app_m.get("latency_p99", 0.0))
                satisfactory = observed <= ind.target_value
            elif ind.sli_type == SLIType.LIVE_PROBE:
                observed = 1.0 if health_m.get("live", True) else 0.0
                satisfactory = observed >= ind.target_value
            elif ind.sli_type == SLIType.READY_PROBE:
                observed = 1.0 if health_m.get("ready", True) else 0.0
                satisfactory = observed >= ind.target_value
            elif ind.sli_type == SLIType.HEALTH_PROBE:
                observed = 1.0 if health_m.get("health", True) else 0.0
                satisfactory = observed >= ind.target_value
            elif ind.sli_type == SLIType.DEPENDENCY_AVAILABILITY:
                dep_ok = all(
                    isinstance(v, dict) and v.get("status") in ("HEALTHY", "AVAILABLE")
                    for v in dep_m.values()
                ) if dep_m else True
                observed = 1.0 if dep_ok else 0.0
                satisfactory = observed >= ind.target_value

            res = SLIResult(
                sli_type=ind.sli_type,
                name=ind.name,
                observed_value=observed,
                target_value=ind.target_value,
                is_satisfactory=satisfactory,
                evidence_level=ev_level,
                details={
                    "indicator": ind.to_dict(),
                    "evidence_level": ev_level,
                },
            )
            results.append(res)
        return results
