"""
Phase 5.70 - Retry Policy Module.

Implements bounded retry policies (MAX_ATTEMPTS, FIXED_DELAY, EXPONENTIAL_BACKOFF) with deterministic backoff calculation and infinite loop prevention.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.reliability.reliability_evidence import ReliabilityEvidenceLevel


class RetryBackoffType(str, Enum):
    FIXED_DELAY = "FIXED_DELAY"
    EXPONENTIAL_BACKOFF = "EXPONENTIAL_BACKOFF"


@dataclass
class RetryPolicyConfig:
    max_attempts: int = 3
    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    backoff_factor: float = 2.0
    backoff_type: RetryBackoffType = RetryBackoffType.EXPONENTIAL_BACKOFF


@dataclass
class RetryPolicyResult:
    total_attempts: int
    max_attempts: int
    success: bool
    final_delay_seconds: float
    total_duration_seconds: float
    retry_history: List[Dict[str, Any]]
    evidence_level: ReliabilityEvidenceLevel


class RetryPolicyEngine:
    """Calculates deterministic delays and bounds retry iterations."""

    def __init__(
        self,
        config: Optional[RetryPolicyConfig] = None,
        evidence_level: ReliabilityEvidenceLevel = ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
    ) -> None:
        self.config = config or RetryPolicyConfig()
        self.evidence_level = evidence_level

    def calculate_delay(self, attempt_index: int) -> float:
        """Calculates backoff delay for 1-based attempt index."""
        if attempt_index <= 1:
            return 0.0

        if self.config.backoff_type == RetryBackoffType.FIXED_DELAY:
            delay = self.config.initial_delay_seconds
        else:
            # Exponential backoff: initial * (factor ^ (attempt - 2))
            delay = self.config.initial_delay_seconds * (self.config.backoff_factor ** (attempt_index - 2))

        return min(delay, self.config.max_delay_seconds)

    def execute_retry_simulation(
        self,
        fail_until_attempt: int = 2,
        executed: bool = True,
    ) -> RetryPolicyResult:
        if not executed:
            return RetryPolicyResult(
                total_attempts=0,
                max_attempts=self.config.max_attempts,
                success=False,
                final_delay_seconds=0.0,
                total_duration_seconds=0.0,
                retry_history=[],
                evidence_level=self.evidence_level,
            )

        history: List[Dict[str, Any]] = []
        total_duration = 0.0
        success = False

        # Strictly bounded loop to prevent infinite retries
        for attempt in range(1, self.config.max_attempts + 1):
            delay = self.calculate_delay(attempt)
            total_duration += delay

            if attempt >= fail_until_attempt:
                success = True
                history.append({"attempt": attempt, "delay": delay, "status": "SUCCESS"})
                break
            else:
                history.append({"attempt": attempt, "delay": delay, "status": "FAILED"})

        return RetryPolicyResult(
            total_attempts=len(history),
            max_attempts=self.config.max_attempts,
            success=success,
            final_delay_seconds=history[-1]["delay"] if history else 0.0,
            total_duration_seconds=total_duration,
            retry_history=history,
            evidence_level=self.evidence_level,
        )
