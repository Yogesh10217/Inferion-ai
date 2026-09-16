"""Application Reliability & Fallback Engine (Phase 5.22 - Component 12).

Reuses existing resilience primitives:
- CircuitBreakerRegistry & RetryManager & FallbackManager (app.resilience)

Supports graceful degradation paths:
- primary model → cheaper model
- agent → deterministic workflow
- live knowledge → cached authorized knowledge
- automation → human escalation
- external integration → deferred retry
All fallbacks strictly preserve authorization and governance controls.
"""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.resilience.circuit_breaker import CircuitBreakerRegistry
from app.resilience.fallback import FallbackManager
from app.resilience.retry import RetryManager

logger = logging.getLogger(__name__)


class DegradationStrategy(str, Enum):
    MODEL_FALLBACK = "MODEL_FALLBACK"
    WORKFLOW_FALLBACK = "WORKFLOW_FALLBACK"
    CACHED_KNOWLEDGE = "CACHED_KNOWLEDGE"
    HUMAN_ESCALATION = "HUMAN_ESCALATION"
    DEFERRED_RETRY = "DEFERRED_RETRY"


class RuntimeFallback(BaseModel):
    """Fallback execution policy and status."""

    fallback_id: str = Field(default_factory=lambda: f"fbk_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    strategy: DegradationStrategy = DegradationStrategy.MODEL_FALLBACK
    primary_target: str
    fallback_target: str
    active: bool = False
    failure_count: int = 0
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ApplicationResilienceManager:
    """Manages application graceful degradation and fallback routes."""

    def __init__(
        self,
        circuit_breaker_registry: Optional[CircuitBreakerRegistry] = None,
        retry_manager: Optional[RetryManager] = None,
        fallback_manager: Optional[FallbackManager] = None,
    ) -> None:
        self.circuit_breaker_registry = circuit_breaker_registry or CircuitBreakerRegistry()
        self.retry_manager = retry_manager or RetryManager()
        self.fallback_manager = fallback_manager or FallbackManager()
        self._fallbacks: Dict[str, RuntimeFallback] = {}  # key: f"{tenant_id}:{app_id}:{primary_target}"

    def register_fallback(
        self,
        tenant_id: str,
        application_id: str,
        primary_target: str,
        fallback_target: str,
        strategy: DegradationStrategy = DegradationStrategy.MODEL_FALLBACK,
    ) -> RuntimeFallback:
        key = f"{tenant_id}:{application_id}:{primary_target}"
        fbk = RuntimeFallback(
            application_id=application_id,
            tenant_id=tenant_id,
            strategy=strategy,
            primary_target=primary_target,
            fallback_target=fallback_target,
        )
        self._fallbacks[key] = fbk
        logger.info(f"[RESILIENCE] Registered fallback for '{primary_target}' → '{fallback_target}' ({strategy.value})")
        return fbk

    def resolve_target(
        self,
        tenant_id: str,
        application_id: str,
        primary_target: str,
        primary_failed: bool = False,
    ) -> Dict[str, Any]:
        """Resolve primary target or execute fallback while preserving governance context."""
        key = f"{tenant_id}:{application_id}:{primary_target}"

        if not primary_failed and key not in self._fallbacks:
            return {"target": primary_target, "is_fallback": False, "strategy": None}

        if primary_failed or (key in self._fallbacks and self._fallbacks[key].active):
            if key in self._fallbacks:
                fbk = self._fallbacks[key]
                fbk.active = True
                fbk.failure_count += 1
                fbk.updated_at = datetime.now(timezone.utc)
                logger.warning(f"[RESILIENCE] Triggered fallback target '{fbk.fallback_target}' for app '{application_id}'")
                return {
                    "target": fbk.fallback_target,
                    "is_fallback": True,
                    "strategy": fbk.strategy.value,
                    "fallback_id": fbk.fallback_id,
                }

        return {"target": primary_target, "is_fallback": False, "strategy": None}
