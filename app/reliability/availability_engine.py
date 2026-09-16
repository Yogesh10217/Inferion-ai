"""
Phase 5.70 - Availability Engine Module.

Evaluates system uptime, service health, dependency availability, degraded operation, and recovery periods.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class AvailabilityClassification(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNAVAILABLE = "UNAVAILABLE"
    UNKNOWN = "UNKNOWN"
    NOT_EXECUTED = "NOT_EXECUTED"


@dataclass
class AvailabilityResult:
    uptime_percentage: float
    classification: AvailabilityClassification
    total_time_seconds: float
    uptime_seconds: float
    downtime_seconds: float
    degraded_seconds: float
    details: Dict[str, Any]
    evidence_level: ReliabilityEvidenceLevel


class AvailabilityEvaluator:
    """Evaluates availability metrics deterministically with zero division protection."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def evaluate_availability(
        self,
        uptime_seconds: float,
        downtime_seconds: float,
        degraded_seconds: float = 0.0,
        executed: bool = True,
        dependencies_healthy: bool = True,
    ) -> AvailabilityResult:
        if not executed:
            return AvailabilityResult(
                uptime_percentage=0.0,
                classification=AvailabilityClassification.NOT_EXECUTED,
                total_time_seconds=0.0,
                uptime_seconds=0.0,
                downtime_seconds=0.0,
                degraded_seconds=0.0,
                details={"message": "Availability evaluation not executed."},
                evidence_level=self.evidence_level,
            )

        total_seconds = uptime_seconds + downtime_seconds + degraded_seconds

        # Protection against division by zero
        if total_seconds <= 0.0:
            return AvailabilityResult(
                uptime_percentage=0.0,
                classification=AvailabilityClassification.UNKNOWN,
                total_time_seconds=0.0,
                uptime_seconds=0.0,
                downtime_seconds=0.0,
                degraded_seconds=0.0,
                details={"message": "Total monitored time must be greater than zero."},
                evidence_level=self.evidence_level,
            )

        uptime_percentage = round((uptime_seconds / total_seconds) * 100.0, 4)

        if downtime_seconds > 0 and uptime_seconds == 0:
            classification = AvailabilityClassification.UNAVAILABLE
        elif degraded_seconds > 0 or not dependencies_healthy or uptime_percentage < 99.0:
            classification = AvailabilityClassification.DEGRADED
        elif uptime_percentage >= 99.0:
            classification = AvailabilityClassification.HEALTHY
        else:
            classification = AvailabilityClassification.DEGRADED

        return AvailabilityResult(
            uptime_percentage=uptime_percentage,
            classification=classification,
            total_time_seconds=total_seconds,
            uptime_seconds=uptime_seconds,
            downtime_seconds=downtime_seconds,
            degraded_seconds=degraded_seconds,
            details={
                "uptime_percentage": uptime_percentage,
                "dependencies_healthy": dependencies_healthy,
            },
            evidence_level=self.evidence_level,
        )
