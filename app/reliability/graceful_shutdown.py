"""Graceful Shutdown Manager for Coordinated Platform Drain & Teardown."""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)


class GracefulShutdownManager:
    """Coordinates multi-phase graceful shutdown: request draining, worker pausing, job checkpointing, telemetry flushing."""

    def __init__(self, drain_timeout_seconds: float = 15.0) -> None:
        self.drain_timeout = drain_timeout_seconds
        self.is_shutting_down: bool = False
        self._active_requests: int = 0
        self._shutdown_hooks: List[Callable] = []

    def register_shutdown_hook(self, hook: Callable) -> None:
        """Register async or sync cleanup callback."""
        self._shutdown_hooks.append(hook)

    def increment_active_requests(self) -> None:
        if self.is_shutting_down:
            raise RuntimeError("Server is shutting down. Rejecting new incoming requests.")
        self._active_requests += 1

    def decrement_active_requests(self) -> None:
        self._active_requests = max(0, self._active_requests - 1)

    async def initiate_shutdown(self) -> Dict[str, Any]:
        """Trigger coordinated graceful shutdown sequence."""
        start_t = time.time()
        self.is_shutting_down = True
        logger.info("[SHUTDOWN] Initiating graceful shutdown sequence...")

        # Phase 1: Drain in-flight HTTP/RPC requests
        drain_start = time.time()
        while self._active_requests > 0 and (time.time() - drain_start) < self.drain_timeout:
            logger.info(f"[SHUTDOWN DRAIN] Waiting for {self._active_requests} active requests to complete...")
            await asyncio.sleep(0.5)

        if self._active_requests > 0:
            logger.warning(f"[SHUTDOWN DRAIN TIMEOUT] Forcibly closing {self._active_requests} remaining active requests")

        # Phase 2: Execute registered shutdown hooks
        for idx, hook in enumerate(self._shutdown_hooks):
            try:
                logger.info(f"[SHUTDOWN HOOK] Executing shutdown hook #{idx + 1}...")
                if asyncio.iscoroutinefunction(hook):
                    await hook()
                else:
                    hook()
            except Exception as exc:
                logger.error(f"[SHUTDOWN HOOK ERROR] Hook #{idx + 1} failed: {exc}")

        dur_ms = (time.time() - start_t) * 1000.0
        logger.info(f"[SHUTDOWN COMPLETE] Graceful shutdown finished in {dur_ms:.1f}ms")
        return {
            "status": "SHUTDOWN_COMPLETED",
            "duration_ms": round(dur_ms, 2),
            "remaining_active_requests": self._active_requests,
        }
