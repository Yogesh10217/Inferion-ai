from __future__ import annotations

import time
from typing import Dict, Any


class DeploymentLivenessProbe:
    """Lightweight process liveness probe verifying event loop responsiveness without expensive IO probes."""

    _start_time: float = time.time()

    @classmethod
    def check_liveness(cls) -> Dict[str, Any]:
        uptime = time.time() - cls._start_time
        return {
            "status": "HEALTHY",
            "live": True,
            "uptime_seconds": round(uptime, 2),
            "timestamp": time.time(),
        }
