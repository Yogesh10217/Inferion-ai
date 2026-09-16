import random
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class RetryPolicy:
    max_retries: int = 5
    initial_interval_ms: int = 1000
    max_interval_ms: int = 300000  # 5 minutes
    backoff_factor: float = 2.0
    jitter_ratio: float = 0.2
    retryable_status_codes: List[int] = field(
        default_factory=lambda: [408, 429, 500, 502, 503, 504]
    )

    def calculate_delay_ms(self, attempt: int) -> float:
        """
        Calculate backoff delay for given attempt (1-indexed).
        Applies exponential backoff and randomized jitter.
        """
        if attempt <= 0:
            return 0.0

        # Calculate base exponential backoff
        interval = self.initial_interval_ms * (self.backoff_factor ** (attempt - 1))
        interval = min(interval, float(self.max_interval_ms))

        # Apply jitter
        if self.jitter_ratio > 0:
            jitter_range = interval * self.jitter_ratio
            interval = interval + random.uniform(-jitter_range, jitter_range)

        return max(0.0, interval)

    def should_retry(self, attempt: int, status_code: Optional[int]) -> bool:
        """Determine if a request should be retried based on attempt count and status code."""
        if attempt >= self.max_retries:
            return False

        # If network error / timeout (status_code is None), retry
        if status_code is None:
            return True

        return status_code in self.retryable_status_codes

    def to_dict(self) -> dict:
        return {
            "max_retries": self.max_retries,
            "initial_interval_ms": self.initial_interval_ms,
            "max_interval_ms": self.max_interval_ms,
            "backoff_factor": self.backoff_factor,
            "jitter_ratio": self.jitter_ratio,
            "retryable_status_codes": self.retryable_status_codes,
        }

    @classmethod
    def from_dict(cls, data: Optional[dict]) -> "RetryPolicy":
        if not data:
            return cls()
        return cls(
            max_retries=data.get("max_retries", 5),
            initial_interval_ms=data.get("initial_interval_ms", 1000),
            max_interval_ms=data.get("max_interval_ms", 300000),
            backoff_factor=data.get("backoff_factor", 2.0),
            jitter_ratio=data.get("jitter_ratio", 0.2),
            retryable_status_codes=data.get("retryable_status_codes", [408, 429, 500, 502, 503, 504]),
        )
