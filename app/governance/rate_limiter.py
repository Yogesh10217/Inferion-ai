"""Enterprise Rate Limiter with Token Bucket & Sliding Window Algorithms."""

import time
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from app.security.exceptions import RateLimitExceededError

logger = logging.getLogger(__name__)


class RateLimitAlgorithm(str, Enum):
    TOKEN_BUCKET = "token_bucket"
    SLIDING_WINDOW = "sliding_window"


class RateLimitPolicy(BaseModel):
    """Configuration for a rate limiting rule."""

    key_prefix: str = "rate"
    max_requests: int = 100
    window_seconds: int = 60
    algorithm: RateLimitAlgorithm = RateLimitAlgorithm.SLIDING_WINDOW
    burst_capacity: Optional[int] = None


class RateLimitResult(BaseModel):
    """Evaluation result of rate limit check."""

    allowed: bool
    limit: int
    remaining: int
    reset_seconds: float
    retry_after_seconds: float = 0.0


class RateLimiter:
    """Distributed-ready rate limiter enforcing Token Bucket & Sliding Window limits."""

    def __init__(self) -> None:
        # In-memory storage structures: key -> state dict
        self._sliding_windows: Dict[str, List[float]] = {}
        self._token_buckets: Dict[str, Dict[str, float]] = {}

    def _build_key(
        self,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        tool: Optional[str] = None,
        worker: Optional[str] = None,
        policy_prefix: str = "rate",
    ) -> str:
        parts = [policy_prefix]
        if tenant_id: parts.append(f"t:{tenant_id}")
        if organization_id: parts.append(f"o:{organization_id}")
        if workspace_id: parts.append(f"w:{workspace_id}")
        if user_id: parts.append(f"u:{user_id}")
        if api_key_id: parts.append(f"k:{api_key_id}")
        if ip_address: parts.append(f"ip:{ip_address}")
        if endpoint: parts.append(f"ep:{endpoint}")
        if model: parts.append(f"m:{model}")
        if tool: parts.append(f"tl:{tool}")
        if worker: parts.append(f"wk:{worker}")
        return ":".join(parts)

    def check(
        self,
        policy: RateLimitPolicy,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        tool: Optional[str] = None,
        worker: Optional[str] = None,
        cost: int = 1,
    ) -> RateLimitResult:
        """Check if request is allowed without consuming tokens."""
        return self.consume(
            policy=policy,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            api_key_id=api_key_id,
            ip_address=ip_address,
            endpoint=endpoint,
            model=model,
            tool=tool,
            worker=worker,
            cost=cost,
            peek_only=True,
        )

    def consume(
        self,
        policy: RateLimitPolicy,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        endpoint: Optional[str] = None,
        model: Optional[str] = None,
        tool: Optional[str] = None,
        worker: Optional[str] = None,
        cost: int = 1,
        peek_only: bool = False,
    ) -> RateLimitResult:
        """Consume tokens/units against rate limit policy."""
        key = self._build_key(
            tenant_id, organization_id, workspace_id, user_id, api_key_id,
            ip_address, endpoint, model, tool, worker, policy.key_prefix
        )
        now = time.time()

        if policy.algorithm == RateLimitAlgorithm.SLIDING_WINDOW:
            return self._consume_sliding_window(key, policy, cost, now, peek_only)
        else:
            return self._consume_token_bucket(key, policy, cost, now, peek_only)

    def _consume_sliding_window(
        self, key: str, policy: RateLimitPolicy, cost: int, now: float, peek_only: bool
    ) -> RateLimitResult:
        if key not in self._sliding_windows:
            self._sliding_windows[key] = []

        window = self._sliding_windows[key]
        cutoff = now - policy.window_seconds
        # Clean expired timestamps
        self._sliding_windows[key] = [t for t in window if t > cutoff]
        window = self._sliding_windows[key]

        current_usage = len(window)
        remaining = max(0, policy.max_requests - current_usage)
        allowed = (current_usage + cost) <= policy.max_requests

        if allowed and not peek_only:
            for _ in range(cost):
                window.append(now)
            remaining = max(0, policy.max_requests - len(window))

        reset_sec = float(policy.window_seconds) if not window else max(0.0, policy.window_seconds - (now - window[0]))
        retry_after = reset_sec if not allowed else 0.0

        if not allowed:
            logger.warning(f"[RATE LIMIT] Policy '{policy.key_prefix}' exceeded for key '{key}'")

        return RateLimitResult(
            allowed=allowed,
            limit=policy.max_requests,
            remaining=remaining,
            reset_seconds=round(reset_sec, 2),
            retry_after_seconds=round(retry_after, 2),
        )

    def _consume_token_bucket(
        self, key: str, policy: RateLimitPolicy, cost: int, now: float, peek_only: bool
    ) -> RateLimitResult:
        capacity = policy.burst_capacity or policy.max_requests
        refill_rate = float(policy.max_requests) / float(policy.window_seconds)

        if key not in self._token_buckets:
            self._token_buckets[key] = {"tokens": float(capacity), "last_refill": now}

        bucket = self._token_buckets[key]
        elapsed = now - bucket["last_refill"]
        bucket["tokens"] = min(float(capacity), bucket["tokens"] + elapsed * refill_rate)
        bucket["last_refill"] = now

        allowed = bucket["tokens"] >= cost
        remaining = int(max(0, bucket["tokens"] - (cost if allowed and not peek_only else 0)))

        if allowed and not peek_only:
            bucket["tokens"] -= cost

        needed = cost - bucket["tokens"]
        retry_after = (needed / refill_rate) if needed > 0 else 0.0

        return RateLimitResult(
            allowed=allowed,
            limit=capacity,
            remaining=remaining,
            reset_seconds=round(retry_after, 2),
            retry_after_seconds=round(retry_after, 2),
        )

    def reset(self, key: str) -> None:
        """Reset rate limit tracking for a given key."""
        self._sliding_windows.pop(key, None)
        self._token_buckets.pop(key, None)

    def get_remaining(self, key: str, policy: RateLimitPolicy) -> int:
        """Get remaining requests in current window for key."""
        res = self.check(policy=policy, tenant_id=key)
        return res.remaining
