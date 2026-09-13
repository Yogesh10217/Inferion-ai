"""
Phase 5.70 - Reliability Metrics Module.

Calculates key Reliability, Resilience, and Chaos metrics deterministically with zero division protection.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


@dataclass
class ReliabilityMetricsResult:
    availability_percentage: float
    failure_rate_percentage: float
    recovery_rate_percentage: float
    mean_time_to_detect_seconds: float
    mean_time_to_acknowledge_seconds: float
    mean_time_to_recover_seconds: float
    resilience_score: float
    recovery_success_rate: float
    chaos_experiment_success_rate: float
    slo_compliance_percentage: float
    evidence_level: ReliabilityEvidenceLevel
    details: Dict[str, Any] = field(default_factory=dict)


class ReliabilityMetricsCalculator:
    """Calculates SRE reliability and chaos engineering metrics deterministically."""

    def __init__(self, evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME) -> None:
        self.evidence_level = evidence_level

    def calculate_metrics(
        self,
        total_uptime_seconds: float = 86300.0,
        total_downtime_seconds: float = 100.0,
        total_requests: int = 1000,
        failed_requests: int = 2,
        successful_recoveries: int = 10,
        failed_recoveries: int = 0,
        successful_chaos_experiments: int = 5,
        failed_chaos_experiments: int = 0,
        detection_latencies: Optional[List[float]] = None,
        ack_latencies: Optional[List[float]] = None,
        recovery_latencies: Optional[List[float]] = None,
        slo_met_count: int = 10,
        total_slo_count: int = 10,
        resilience_score_input: float = 100.0,
        executed: bool = True,
    ) -> ReliabilityMetricsResult:
        if not executed:
            return ReliabilityMetricsResult(
                availability_percentage=0.0,
                failure_rate_percentage=0.0,
                recovery_rate_percentage=0.0,
                mean_time_to_detect_seconds=0.0,
                mean_time_to_acknowledge_seconds=0.0,
                mean_time_to_recover_seconds=0.0,
                resilience_score=0.0,
                recovery_success_rate=0.0,
                chaos_experiment_success_rate=0.0,
                slo_compliance_percentage=0.0,
                evidence_level=self.evidence_level,
                details={"message": "Metrics calculation not executed."},
            )

        # 1. Availability
        total_time = total_uptime_seconds + total_downtime_seconds
        avail_pct = round((total_uptime_seconds / total_time) * 100.0, 4) if total_time > 0 else 0.0

        # 2. Failure Rate
        fail_rate = round((failed_requests / total_requests) * 100.0, 4) if total_requests > 0 else 0.0

        # 3. Recovery Success & Rate
        tot_rec = successful_recoveries + failed_recoveries
        rec_rate = round((successful_recoveries / tot_rec) * 100.0, 2) if tot_rec > 0 else 100.0

        # 4. Chaos Success Rate
        tot_chaos = successful_chaos_experiments + failed_chaos_experiments
        chaos_rate = round((successful_chaos_experiments / tot_chaos) * 100.0, 2) if tot_chaos > 0 else 100.0

        # 5. Latencies (MTTD, MTTA, MTTR)
        det_lats = detection_latencies or [30.0]
        mttd = round(sum(det_lats) / len(det_lats), 2) if len(det_lats) > 0 else 0.0

        ack_lats = ack_latencies or [120.0]
        mtta = round(sum(ack_lats) / len(ack_lats), 2) if len(ack_lats) > 0 else 0.0

        rec_lats = recovery_latencies or [300.0]
        mttr = round(sum(rec_lats) / len(rec_lats), 2) if len(rec_lats) > 0 else 0.0

        # 6. SLO Compliance
        slo_comp = round((slo_met_count / total_slo_count) * 100.0, 2) if total_slo_count > 0 else 100.0

        return ReliabilityMetricsResult(
            availability_percentage=avail_pct,
            failure_rate_percentage=fail_rate,
            recovery_rate_percentage=rec_rate,
            mean_time_to_detect_seconds=mttd,
            mean_time_to_acknowledge_seconds=mtta,
            mean_time_to_recover_seconds=mttr,
            resilience_score=resilience_score_input,
            recovery_success_rate=rec_rate,
            chaos_experiment_success_rate=chaos_rate,
            slo_compliance_percentage=slo_comp,
            evidence_level=self.evidence_level,
            details={"monitored_seconds": total_time},
        )
