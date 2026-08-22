"""Fallback Manager for Degraded Modes & Multi-Tier Fallback Strategies."""

import logging
import asyncio
from enum import Enum
from typing import Dict, Any, Callable, Optional, List, Union
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FallbackMode(str, Enum):
    PROVIDER_FALLBACK = "provider_fallback"
    MODEL_FALLBACK = "model_fallback"
    CACHE_FALLBACK = "cache_fallback"
    DEGRADED_RESPONSE = "degraded_response"


class FallbackStrategy(BaseModel):
    """Configuration defining fallback cascade order."""

    fallback_providers: List[str] = Field(default_factory=list)
    fallback_models: List[str] = Field(default_factory=list)
    enable_cache_fallback: bool = True
    enable_degraded_mode: bool = True
    default_degraded_response: Dict[str, Any] = Field(
        default_factory=lambda: {
            "content": "Service is operating in degraded mode. Primary model output temporarily unavailable.",
            "is_degraded": True,
            "status": "degraded_success",
        }
    )


class FallbackManager:
    """Orchestrates primary execution and multi-tiered fallback strategies upon component failure."""

    def __init__(self, strategy: Optional[FallbackStrategy] = None) -> None:
        self.strategy = strategy or FallbackStrategy()

    async def execute_with_fallback(
        self,
        primary_func: Callable,
        fallback_funcs: Optional[List[Callable]] = None,
        cache_lookup_func: Optional[Callable] = None,
        strategy: Optional[FallbackStrategy] = None,
        *args,
        **kwargs,
    ) -> Any:
        pol = strategy or self.strategy

        # Tier 1: Try Primary execution
        try:
            if asyncio.iscoroutinefunction(primary_func):
                return await primary_func(*args, **kwargs)
            else:
                return primary_func(*args, **kwargs)
        except Exception as primary_exc:
            logger.warning(f"[FALLBACK TIER 1 FAILED] Primary function error: {primary_exc}")

        # Tier 2: Try Secondary/Fallback Callables
        if fallback_funcs:
            for idx, fb_func in enumerate(fallback_funcs):
                try:
                    logger.info(f"[FALLBACK TIER 2] Attempting fallback candidate #{idx + 1}...")
                    if asyncio.iscoroutinefunction(fb_func):
                        return await fb_func(*args, **kwargs)
                    else:
                        return fb_func(*args, **kwargs)
                except Exception as fb_exc:
                    logger.warning(f"[FALLBACK TIER 2 FAILED] Fallback candidate #{idx + 1} failed: {fb_exc}")

        # Tier 3: Try Cache lookup if configured
        if pol.enable_cache_fallback and cache_lookup_func:
            try:
                logger.info("[FALLBACK TIER 3] Attempting cache lookup fallback...")
                cached = await cache_lookup_func(*args, **kwargs) if asyncio.iscoroutinefunction(cache_lookup_func) else cache_lookup_func(*args, **kwargs)
                if cached:
                    logger.info("[FALLBACK TIER 3 SUCCESS] Cache fallback response retrieved")
                    return cached
            except Exception as cache_exc:
                logger.warning(f"[FALLBACK TIER 3 FAILED] Cache fallback failed: {cache_exc}")

        # Tier 4: Graceful Degraded Response
        if pol.enable_degraded_mode:
            logger.warning("[FALLBACK TIER 4] Returning graceful degraded response")
            return pol.default_degraded_response

        raise RuntimeError("All fallback options exhausted and degraded mode disabled")
