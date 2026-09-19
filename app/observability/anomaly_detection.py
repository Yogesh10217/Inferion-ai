"""AIOps Statistical Anomaly Detection Subsystem."""

from __future__ import annotations

import logging
import math
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class AnomalyEvent:
    """Structured anomaly notification event."""

    anomaly_id: str
    metric_name: str
    anomaly_type: str  # COST_SPIKE, LATENCY_SPIKE, FAILURE_SPIKE, EXECUTION_LOOP, DEGRADATION
    severity: str  # WARNING, CRITICAL
    current_value: float
    baseline_value: float
    threshold: float
    component: str
    message: str
    timestamp: float = field(default_factory=time.time)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AnomalyDetector:
    """Detects metric anomalies using moving averages, z-score thresholds, and execution loop analysis."""

    def __init__(self, z_threshold: float = 3.0, cost_spike_multiplier: float = 2.5) -> None:
        self.z_threshold = z_threshold
        self.cost_spike_multiplier = cost_spike_multiplier
        self._baselines: Dict[str, List[float]] = {}
        self._detected_anomalies: List[AnomalyEvent] = []

    def establish_baseline(self, metric_name: str, values: List[float]) -> Dict[str, float]:
        """Establish or update moving statistical baseline for a metric."""
        if not values:
            return {"mean": 0.0, "stddev": 0.0, "count": 0}

        self._baselines[metric_name] = values
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values) if len(values) > 1 else 0.0
        stddev = math.sqrt(variance)

        return {"mean": round(mean, 4), "stddev": round(stddev, 4), "count": len(values)}

    def detect_cost_spike(
        self,
        component: str,
        current_cost: float,
        historical_costs: Optional[List[float]] = None,
    ) -> Optional[AnomalyEvent]:
        """Detect sudden token or monetary cost spike."""
        history = historical_costs or self._baselines.get(f"{component}.cost", [])
        if not history:
            return None

        avg_cost = sum(history) / len(history)
        threshold = avg_cost * self.cost_spike_multiplier

        if current_cost > threshold and current_cost > 0.01:
            evt = AnomalyEvent(
                anomaly_id=f"anom-cost-{int(time.time())}",
                metric_name="cost",
                anomaly_type="COST_SPIKE",
                severity="CRITICAL" if current_cost > threshold * 2 else "WARNING",
                current_value=round(current_cost, 4),
                baseline_value=round(avg_cost, 4),
                threshold=round(threshold, 4),
                component=component,
                message=f"Cost spike detected in {component}: ${current_cost:.4f} exceeds baseline avg ${avg_cost:.4f} by >{self.cost_spike_multiplier}x.",
            )
            self._detected_anomalies.append(evt)
            return evt
        return None

    def detect_latency_spike(
        self,
        component: str,
        current_latency_ms: float,
        historical_latencies: Optional[List[float]] = None,
    ) -> Optional[AnomalyEvent]:
        """Detect latency degradation or spike using z-score."""
        history = historical_latencies or self._baselines.get(f"{component}.latency", [])
        if len(history) < 3:
            return None

        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / len(history)
        stddev = math.sqrt(variance) if variance > 0 else 1.0

        z_score = (current_latency_ms - mean) / stddev

        if z_score >= self.z_threshold and current_latency_ms > mean + 500:
            threshold = round(mean + (self.z_threshold * stddev), 2)
            evt = AnomalyEvent(
                anomaly_id=f"anom-lat-{int(time.time())}",
                metric_name="latency_ms",
                anomaly_type="LATENCY_SPIKE",
                severity="CRITICAL" if z_score > 4.0 else "WARNING",
                current_value=round(current_latency_ms, 2),
                baseline_value=round(mean, 2),
                threshold=threshold,
                component=component,
                message=f"Latency spike in {component}: {current_latency_ms:.1f}ms (z-score: {z_score:.2f}) exceeds baseline {mean:.1f}ms.",
            )
            self._detected_anomalies.append(evt)
            return evt
        return None

    def detect_failure_spike(
        self,
        component: str,
        current_error_rate: float,
        baseline_error_rate: float = 0.05,
    ) -> Optional[AnomalyEvent]:
        """Detect sudden surge in component failure rate."""
        if current_error_rate >= baseline_error_rate * 3.0 and current_error_rate > 0.15:
            evt = AnomalyEvent(
                anomaly_id=f"anom-fail-{int(time.time())}",
                metric_name="error_rate",
                anomaly_type="FAILURE_SPIKE",
                severity="CRITICAL",
                current_value=round(current_error_rate, 4),
                baseline_value=round(baseline_error_rate, 4),
                threshold=round(baseline_error_rate * 3.0, 4),
                component=component,
                message=f"Failure rate spike in {component}: {current_error_rate * 100:.1f}% error rate exceeds threshold {baseline_error_rate * 3 * 100:.1f}%.",
            )
            self._detected_anomalies.append(evt)
            return evt
        return None

    def detect_execution_loop(
        self,
        span_names: List[str],
        max_repeats: int = 5,
        component: str = "agent",
    ) -> Optional[AnomalyEvent]:
        """Detect infinite tool or workflow loop patterns in span sequences."""
        if len(span_names) < max_repeats:
            return None

        # Check for trailing repetition of identical span name
        last_item = span_names[-1]
        repeats = 0
        for item in reversed(span_names):
            if item == last_item:
                repeats += 1
            else:
                break

        if repeats >= max_repeats:
            evt = AnomalyEvent(
                anomaly_id=f"anom-loop-{int(time.time())}",
                metric_name="repeated_spans",
                anomaly_type="EXECUTION_LOOP",
                severity="CRITICAL",
                current_value=float(repeats),
                baseline_value=1.0,
                threshold=float(max_repeats),
                component=component,
                message=f"Unexpected execution loop detected in {component}: step '{last_item}' repeated {repeats} times sequentially.",
            )
            self._detected_anomalies.append(evt)
            return evt
        return None

    def detect_anomalies(
        self,
        component: str,
        latency_ms: Optional[float] = None,
        cost: Optional[float] = None,
        error_rate: Optional[float] = None,
        span_history: Optional[List[str]] = None,
    ) -> List[AnomalyEvent]:
        """Run all anomaly detection checks for a component."""
        found: List[AnomalyEvent] = []

        if latency_ms is not None:
            lat_anom = self.detect_latency_spike(component, latency_ms)
            if lat_anom:
                found.append(lat_anom)

        if cost is not None:
            cost_anom = self.detect_cost_spike(component, cost)
            if cost_anom:
                found.append(cost_anom)

        if error_rate is not None:
            fail_anom = self.detect_failure_spike(component, error_rate)
            if fail_anom:
                found.append(fail_anom)

        if span_history:
            loop_anom = self.detect_execution_loop(span_history, component=component)
            if loop_anom:
                found.append(loop_anom)

        return found

    def get_recent_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve recent anomaly events."""
        return [a.to_dict() for a in self._detected_anomalies[-limit:]]
