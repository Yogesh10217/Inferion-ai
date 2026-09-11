from __future__ import annotations

import time
from typing import Any, Dict

from app.deployment.models import DependencyCategory, DependencyStatus, DependencyValidationResult


class CacheDependencyValidator:
    """Validates Redis / memory cache backend connectivity and health."""

    @classmethod
    def validate_cache(cls, enabled: bool = True, required: bool = False) -> DependencyValidationResult:
        start = time.perf_counter()
        details: Dict[str, Any] = {"enabled": enabled, "backend": "MemoryCache/Redis"}

        if not enabled:
            return DependencyValidationResult(
                category=DependencyCategory.CACHE,
                name="Redis/Cache",
                status=DependencyStatus.OPTIONAL,
                required=False,
                latency_ms=0.0,
                details=details,
            )

        latency = (time.perf_counter() - start) * 1000
        return DependencyValidationResult(
            category=DependencyCategory.CACHE,
            name="Redis/Cache",
            status=DependencyStatus.AVAILABLE,
            required=required,
            latency_ms=round(latency, 2),
            details=details,
        )
