"""Workflow Failure Recovery & Exception Handling Strategy Engine."""

import logging
from enum import Enum
from typing import Optional

from app.resilience.fallback import FallbackManager
from app.resilience.retry import RetryManager

logger = logging.getLogger(__name__)


class RecoveryStrategy(str, Enum):
    RETRY = "RETRY"
    FALLBACK = "FALLBACK"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    PAUSE = "PAUSE"
    COMPENSATE = "COMPENSATE"
    ROLLBACK = "ROLLBACK"
    CANCEL = "CANCEL"


class RecoveryManager:
    """Evaluates process execution failures and recommends recovery strategies."""

    def __init__(
        self,
        retry_manager: Optional[RetryManager] = None,
        fallback_manager: Optional[FallbackManager] = None,
    ) -> None:
        self.retry_manager = retry_manager or RetryManager()
        self.fallback_manager = fallback_manager or FallbackManager()

    def handle_failure(
        self,
        execution_id: str,
        step_id: str,
        error_message: str,
        attempt: int = 1,
        max_retries: int = 3,
    ) -> RecoveryStrategy:
        if attempt <= max_retries:
            logger.info(f"[RECOVERY MANAGER] Step '{step_id}' failed (Attempt {attempt}/{max_retries}) -> Strategy: RETRY")
            return RecoveryStrategy.RETRY

        logger.warning(f"[RECOVERY MANAGER] Step '{step_id}' exceeded max retries ({max_retries}) -> Strategy: COMPENSATE")
        return RecoveryStrategy.COMPENSATE
