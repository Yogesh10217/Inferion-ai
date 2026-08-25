"""Observability Conventions & Prometheus Naming Rules (Phase 5.30)."""

import re
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class MetricNameValidator:
    """Validates Prometheus metric naming conventions: ai_<domain>_<resource>_<metric>."""

    PATTERN = re.compile(r"^ai_[a-z0-9_]+_[a-z0-9_]+_[a-z0-9_]+$")

    @classmethod
    def validate_metric_name(cls, metric_name: str) -> bool:
        return bool(cls.PATTERN.match(metric_name))

    @classmethod
    def format_metric_name(cls, domain: str, resource: str, metric: str) -> str:
        clean_dom = domain.lower().replace("-", "_")
        clean_res = resource.lower().replace("-", "_")
        clean_met = metric.lower().replace("-", "_")
        name = f"ai_{clean_dom}_{clean_res}_{clean_met}"
        return name


class SafeMetricLabelSanitizer:
    """Sanitizes high-cardinality and sensitive labels in metrics."""

    @staticmethod
    def sanitize_labels(labels: Dict[str, str]) -> Dict[str, str]:
        safe = {}
        sensitive_keys = {"secret", "token", "password", "key", "auth", "pii", "user_id", "email"}
        for k, v in labels.items():
            if any(sec in k.lower() for sec in sensitive_keys):
                safe[k] = "[REDACTED]"
            else:
                safe[k] = str(v)
        return safe
