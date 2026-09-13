"""
Phase 5.70 - Reliability Metrics Module.

Calculates key Reliability and SRE operational metrics deterministically with zero division protection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


@dataclass
class ReliabilityMetricsResult:
    availability_percentage: float
    recovery_success_rate: float
    failure_detection_rate: float
    mean_time_to_detect_seconds: float
    mean_time_to_acknowledge_seconds: float
    mean_time_to_recover_seconds: float
    recovery_objective_compliance_percentage: float
    dependency_availability_percentage: float
    degradation_success_rate: float
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class ReliabilityMetricsCalculator:
    """Calculates SRE reliability metrics deterministically."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def calculate_metrics(
        self,
        total_uptime_seconds: float = 86400.0,
        total_downtime_seconds: float = 0.0,
        successful_recoveries: int = 10,
        failed_recoveries: int = 0,
        detected_failures: int = 10,
        total_failures: int = 10,
        detection_latencies: Optional[List[float]] = None,
        ack_latencies: Optional[List[float]] = None,
        recovery_latencies: Optional[List[float]] = None,
        objectives_met_count: int = 10,
        total_objectives_count: int = 10,
        healthy_dependencies_count: int = 7,
        total_dependencies_count: int = 7,
        successful_degradations: int = 5,
        total_degradation_events: int = 5,
        executed: bool = True,
    ) -> ReliabilityMetricsResult:
        if not executed:
            return ReliabilityMetricsResult(
                availability_percentage=0.0,
                recovery_success_rate=0.0,
                failure_detection_rate=0.0,
                mean_time_to_detect_seconds=0.0,
                mean_time_to_acknowledge_seconds=0.0,
                mean_time_to_recover_seconds=0.0,
                recovery_objective_compliance_percentage=0.0,
                dependency_availability_percentage=0.0,
                degradation_success_rate=0.0,
                evidence_level=self.evidence_level,
                details={"message": "Metrics calculation not executed."},
            )

        # 1. Availability
        total_time = total_uptime_seconds + total_downtime_seconds
        avail_pct = round((total_uptime_seconds / total_time) * 100.0, 4) if total_time > 0 else 0.0

        # 2. Recovery Success Rate
        tot_rec = successful_recoveries + failed_recoveries
        rec_success_rate = round((successful_recoveries / tot_rec) * 100.0, 2) if tot_rec > 0 else 100.0

        # 3. Failure Detection Rate
        det_rate = round((detected_failures / total_failures) * 100.0, 2) if total_failures > 0 else 100.0

        # 4. Latencies (MTTD, MTTA, MTTR)
        det_lats = detection_latencies or [30.0]
        mttd = round(sum(det_lats) / len(det_lats), 2) if len(det_lats) > 0 else 0.0

        ack_lats = ack_latencies or [120.0]
        mtta = round(sum(ack_lats) / len(ack_lats), 2) if len(ack_lats) > 0 else 0.0

        rec_lats = recovery_latencies or [300.0]
        mttr = round(sum(rec_lats) / len(rec_lats), 2) if len(rec_lats) > 0 else 0.0

        # 5. Recovery Objective Compliance
        obj_comp = round((objectives_met_count / total_objectives_count) * 100.0, 2) if total_objectives_count > 0 else 100.0

        # 6. Dependency Availability
        dep_avail = round((healthy_dependencies_count / total_dependencies_count) * 100.0, 2) if total_dependencies_count > 0 else 100.0

        # 7. Degradation Success Rate
        deg_rate = round((successful_degradations / total_degradation_events) * 100.0, 2) if total_degradation_events > 0 else 100.0

        return ReliabilityMetricsResult(
            availability_percentage=avail_pct,
            recovery_success_rate=rec_success_rate,
            failure_detection_rate=det_rate,
            mean_time_to_detect_seconds=mttd,
            mean_time_to_acknowledge_seconds=mtta,
            mean_time_to_recover_seconds=mttr,
            recovery_objective_compliance_percentage=obj_comp,
            dependency_availability_percentage=dep_avail,
            degradation_success_rate=deg_rate,
            evidence_level=self.evidence_level,
            details={"raw_time_monitored": total_time},
        )
