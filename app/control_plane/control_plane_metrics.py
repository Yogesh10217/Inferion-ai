"""Prometheus Metrics Collector for Control Plane Subsystems."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ControlPlaneMetricsCollector:
    """Prometheus metrics mapper for control plane requests, failures, rollbacks, policy evaluations, and feature rollouts."""

    def __init__(self) -> None:
        self.metrics: Dict[str, float] = {
            "control_plane_requests_total": 0.0,
            "control_plane_failures_total": 0.0,
            "tenants_total": 0.0,
            "organizations_total": 0.0,
            "workspaces_total": 0.0,
            "resources_total": 0.0,
            "configuration_changes_total": 0.0,
            "configuration_rollbacks_total": 0.0,
            "policy_evaluations_total": 0.0,
            "policy_violations_total": 0.0,
            "administrative_operations_total": 0.0,
            "administrative_operation_failures_total": 0.0,
            "feature_rollouts_total": 0.0,
            "resource_provisioning_total": 0.0,
            "resource_provisioning_failures_total": 0.0,
        }

    def increment(self, metric_name: str, value: float = 1.0) -> None:
        if metric_name in self.metrics:
            self.metrics[metric_name] += value
        else:
            self.metrics[metric_name] = value

    def get_metrics_summary(self) -> Dict[str, float]:
        return dict(self.metrics)
