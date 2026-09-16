"""Layered Timeout Manager for Request, Tool, Model, and Service Operations."""

import asyncio
import logging
from typing import Any, Callable, Optional

from pydantic import BaseModel

from app.core.exceptions import AppException

logger = logging.getLogger(__name__)


class TimeoutException(AppException):
    """Raised when an operation exceeds its configured timeout duration."""

    def __init__(self, layer: str, timeout_seconds: float) -> None:
        super().__init__(
            message=f"Operation timed out in layer '{layer}' after {timeout_seconds:.1f}s",
            code="TIMEOUT",
            status_code=504,
            details={"layer": layer, "timeout_seconds": timeout_seconds},
        )


class TimeoutPolicy(BaseModel):
    """Layered timeout policies."""

    request_timeout_seconds: float = 60.0
    model_timeout_seconds: float = 45.0
    provider_timeout_seconds: float = 30.0
    tool_timeout_seconds: float = 20.0
    workflow_timeout_seconds: float = 120.0
    agent_timeout_seconds: float = 90.0
    team_timeout_seconds: float = 180.0
    worker_timeout_seconds: float = 300.0


class TimeoutManager:
    """Enforces timeout boundaries at any execution layer."""

    def __init__(self, policy: Optional[TimeoutPolicy] = None) -> None:
        self.policy = policy or TimeoutPolicy()

    def get_timeout_for_layer(self, layer: str) -> float:
        layer_norm = layer.lower()
        if layer_norm in ("request", "gateway"):
            return self.policy.request_timeout_seconds
        elif layer_norm == "model":
            return self.policy.model_timeout_seconds
        elif layer_norm == "provider":
            return self.policy.provider_timeout_seconds
        elif layer_norm in ("tool", "mcp"):
            return self.policy.tool_timeout_seconds
        elif layer_norm == "workflow":
            return self.policy.workflow_timeout_seconds
        elif layer_norm == "agent":
            return self.policy.agent_timeout_seconds
        elif layer_norm == "team":
            return self.policy.team_timeout_seconds
        elif layer_norm in ("worker", "job"):
            return self.policy.worker_timeout_seconds
        return self.policy.request_timeout_seconds

    async def execute_with_timeout(self, layer: str, func: Callable, *args, custom_timeout: Optional[float] = None, **kwargs) -> Any:
        """Execute async callable under specified layer timeout limit."""
        timeout_sec = custom_timeout if custom_timeout is not None else self.get_timeout_for_layer(layer)
        try:
            if asyncio.iscoroutinefunction(func):
                return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_sec)
            else:
                return await asyncio.wait_for(asyncio.to_thread(func, *args, **kwargs), timeout=timeout_sec)
        except asyncio.TimeoutError:
            logger.warning(f"[TIMEOUT] Layer '{layer}' operation exceeded limit ({timeout_sec}s)")
            raise TimeoutException(layer=layer, timeout_seconds=timeout_sec)
