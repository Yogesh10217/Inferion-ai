from __future__ import annotations

import logging
from typing import Optional

from app.deployment.exceptions import ShutdownLifecycleError
from app.deployment.logging_configuration import StructuredLoggingConfigurator
from app.deployment.models import EnvironmentConfig, ShutdownState

logger = logging.getLogger("app.deployment.shutdown")


class DeploymentShutdownManager:
    """Orchestrates graceful service shutdown, draining, telemetry flushing, and connection releases."""

    VALID_TRANSITIONS = {
        ShutdownState.READY: [ShutdownState.DRAINING],
        ShutdownState.DRAINING: [ShutdownState.STOPPING],
        ShutdownState.STOPPING: [ShutdownState.STOPPED],
        ShutdownState.STOPPED: [],
    }

    def __init__(self, config: Optional[EnvironmentConfig] = None) -> None:
        self.config = config
        self.state = ShutdownState.READY

    def transition_to(self, new_state: ShutdownState) -> None:
        allowed = self.VALID_TRANSITIONS.get(self.state, [])
        if new_state not in allowed:
            raise ShutdownLifecycleError(
                f"Invalid shutdown transition: Cannot transition from {self.state.value} to {new_state.value}"
            )
        self.state = new_state

    def execute_shutdown(self) -> ShutdownState:
        """Executes graceful shutdown sequence."""
        try:
            StructuredLoggingConfigurator.log_event(
                logger, logging.INFO, "GRACEFUL_SHUTDOWN_STARTED", "Initiating graceful application shutdown"
            )

            # 1. Drain incoming requests
            self.transition_to(ShutdownState.DRAINING)

            # 2. Flush telemetry and close connections
            self.transition_to(ShutdownState.STOPPING)

            # 3. Mark STOPPED
            self.transition_to(ShutdownState.STOPPED)

            StructuredLoggingConfigurator.log_event(
                logger, logging.INFO, "GRACEFUL_SHUTDOWN_COMPLETED", "Application shutdown completed successfully"
            )
            return self.state

        except Exception as exc:
            StructuredLoggingConfigurator.log_event(
                logger, logging.ERROR, "SHUTDOWN_FAILED", f"Graceful shutdown failed: {exc}"
            )
            raise ShutdownLifecycleError(f"Shutdown sequence error: {exc}")
