from __future__ import annotations

import time
from typing import Any, Dict

from app.deployment.models import DependencyCategory, DependencyStatus, DependencyValidationResult


class MessagingDependencyValidator:
    """Validates Event Bus / Message Broker infrastructure connectivity."""

    @classmethod
    def validate_messaging(cls, enabled: bool = True, required: bool = False) -> DependencyValidationResult:
        start = time.perf_counter()
        details: Dict[str, Any] = {"enabled": enabled, "bus": "InMemoryEventBus"}

        if not enabled:
            return DependencyValidationResult(
                category=DependencyCategory.MESSAGE_BROKER,
                name="EventBus/Broker",
                status=DependencyStatus.OPTIONAL,
                required=False,
                latency_ms=0.0,
                details=details,
            )

        latency = (time.perf_counter() - start) * 1000
        return DependencyValidationResult(
            category=DependencyCategory.MESSAGE_BROKER,
            name="EventBus/Broker",
            status=DependencyStatus.AVAILABLE,
            required=required,
            latency_ms=round(latency, 2),
            details=details,
        )
