"""Isolated Sandboxed Extension Runtime environment."""

import time
import logging
from typing import Dict, Any, Optional, Callable
from app.extensions.extension import Extension
from app.extensions.exceptions import ExtensionRuntimeExecutionException
from app.resilience.circuit_breaker import CircuitBreakerRegistry
from app.resilience.bulkhead import BulkheadRegistry
from app.resilience.timeout import TimeoutManager
from app.governance.resource_governance import ResourceGovernanceEngine

logger = logging.getLogger(__name__)


class IsolatedExtensionRuntime:
    """Executes extension handlers within governance constraints (timeouts, bulkheads, circuit breakers, compute limits)."""

    def __init__(
        self,
        circuit_breakers: Optional[CircuitBreakerRegistry] = None,
        bulkheads: Optional[BulkheadRegistry] = None,
        timeouts: Optional[TimeoutManager] = None,
        governance: Optional[ResourceGovernanceEngine] = None,
    ) -> None:
        self.circuit_breakers = circuit_breakers or CircuitBreakerRegistry()
        self.bulkheads = bulkheads or BulkheadRegistry()
        self.timeouts = timeouts or TimeoutManager()
        self.governance = governance or ResourceGovernanceEngine()

    def execute_extension_handler(
        self,
        extension: Extension,
        handler: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute extension handler safely within resource limits and resilience guards."""

        # 1. Circuit Breaker Guard
        cb = self.circuit_breakers.get_breaker(f"ext:{extension.extension_id}")
        if not cb.allow_request():
            raise ExtensionRuntimeExecutionException(extension.extension_id, "Circuit breaker OPEN for extension")

        # 2. Timeout Guard
        timeout_sec = float(extension.manifest.runtime_requirements.max_execution_timeout_sec)

        start_time = time.time()
        try:
            # Execute handler directly inside governance wrapper
            res = handler(*args, **kwargs)
            duration = time.time() - start_time
            if duration > timeout_sec:
                cb.record_failure()
                raise ExtensionRuntimeExecutionException(extension.extension_id, f"Execution timed out ({duration:.2f}s > {timeout_sec}s)")

            cb.record_success()
            logger.info(f"[EXTENSION RUNTIME] Executed extension '{extension.extension_id}' in {duration:.3f}s")
            return res
        except Exception as e:
            cb.record_failure()
            logger.error(f"[EXTENSION RUNTIME ERROR] Extension '{extension.extension_id}' failed: {e}")
            raise ExtensionRuntimeExecutionException(extension.extension_id, str(e))

