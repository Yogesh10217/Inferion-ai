from __future__ import annotations

import socket
import time
from typing import Any, Dict

from app.deployment.models import DependencyCategory, DependencyStatus, DependencyValidationResult


from urllib.parse import urlparse

class CacheDependencyValidator:
    """Validates Redis / memory cache backend connectivity and health via real socket probes."""

    @classmethod
    def validate_cache(
        cls,
        enabled: bool = True,
        required: bool = False,
        host: str = "localhost",
        port: int = 6379,
        redis_url: Optional[str] = None,
        timeout_sec: float = 2.0,
    ) -> DependencyValidationResult:
        if redis_url:
            parsed = urlparse(redis_url)
            if parsed.hostname:
                host = parsed.hostname
            if parsed.port:
                port = parsed.port

        start = time.perf_counter()
        details: Dict[str, Any] = {"enabled": enabled, "backend": "Redis", "host": host, "port": port}

        if not enabled:
            return DependencyValidationResult(
                category=DependencyCategory.CACHE,
                name="Redis/Cache",
                status=DependencyStatus.OPTIONAL,
                required=False,
                latency_ms=0.0,
                details=details,
            )

        try:
            with socket.create_connection((host, port), timeout=timeout_sec):
                latency = (time.perf_counter() - start) * 1000
                details["real_socket_connected"] = True
                return DependencyValidationResult(
                    category=DependencyCategory.CACHE,
                    name="Redis/Cache",
                    status=DependencyStatus.AVAILABLE,
                    required=required,
                    latency_ms=round(latency, 2),
                    details=details,
                )
        except Exception as exc:
            latency = (time.perf_counter() - start) * 1000
            details["real_socket_connected"] = False
            status = DependencyStatus.UNAVAILABLE if required else DependencyStatus.DEGRADED
            return DependencyValidationResult(
                category=DependencyCategory.CACHE,
                name="Redis/Cache",
                status=status,
                required=required,
                latency_ms=round(latency, 2),
                details=details,
                error_message=f"TCP connection to Redis ({host}:{port}) failed: {str(exc)}",
            )

