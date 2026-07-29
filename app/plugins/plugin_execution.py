import asyncio
import time
import logging
from typing import Callable, Any, Optional
from prometheus_client import Counter, Histogram, Gauge
from .exceptions import PluginExecutionError, PluginPermissionError

logger = logging.getLogger(__name__)

# Prometheus Metrics for Plugins
PLUGIN_LOAD_TOTAL = Counter("llm_engine_plugin_load_total", "Total plugins loaded", ["plugin_id"])
PLUGIN_EXECUTION_TOTAL = Counter("llm_engine_plugin_execution_total", "Total plugin executions", ["plugin_id", "hook"])
PLUGIN_EXECUTION_DURATION_SECONDS = Histogram(
    "llm_engine_plugin_execution_duration_seconds",
    "Histogram of plugin execution duration",
    ["plugin_id"],
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0),
)
PLUGIN_FAILURES_TOTAL = Counter("llm_engine_plugin_failures_total", "Total plugin failures", ["plugin_id"])
PLUGIN_TIMEOUTS_TOTAL = Counter("llm_engine_plugin_timeouts_total", "Total plugin execution timeouts", ["plugin_id"])
PLUGIN_ENABLED_TOTAL = Gauge("llm_engine_plugin_enabled_total", "Number of currently enabled plugins")
PLUGIN_DISABLED_TOTAL = Gauge("llm_engine_plugin_disabled_total", "Number of currently disabled plugins")


class PluginExecutor:
    """Safely executes plugin functions within timeouts, catching exceptions and reporting metrics."""

    def __init__(self, default_timeout: float = 5.0):
        self.default_timeout = default_timeout

    async def execute(
        self,
        plugin_id: str,
        func: Callable,
        *args,
        hook_name: str = "custom",
        timeout: Optional[float] = None,
        **kwargs,
    ) -> Any:
        timeout_val = timeout if timeout is not None else self.default_timeout
        start_time = time.time()
        PLUGIN_EXECUTION_TOTAL.labels(plugin_id=plugin_id, hook=hook_name).inc()

        try:
            res = await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_val)
            duration = time.time() - start_time
            PLUGIN_EXECUTION_DURATION_SECONDS.labels(plugin_id=plugin_id).observe(duration)
            return res
        except asyncio.TimeoutError:
            logger.error(f"Plugin '{plugin_id}' execution timed out after {timeout_val}s on hook '{hook_name}'")
            PLUGIN_TIMEOUTS_TOTAL.labels(plugin_id=plugin_id).inc()
            PLUGIN_FAILURES_TOTAL.labels(plugin_id=plugin_id).inc()
            raise PluginExecutionError(f"Plugin '{plugin_id}' execution timed out")
        except PluginPermissionError:
            PLUGIN_FAILURES_TOTAL.labels(plugin_id=plugin_id).inc()
            raise
        except Exception as e:
            logger.exception(f"Plugin '{plugin_id}' encountered error during '{hook_name}': {e}")
            PLUGIN_FAILURES_TOTAL.labels(plugin_id=plugin_id).inc()
            raise PluginExecutionError(f"Plugin '{plugin_id}' execution failed: {e}") from e
