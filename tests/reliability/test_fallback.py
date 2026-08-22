"""Unit tests for FallbackManager."""

import pytest
from app.resilience.fallback import FallbackManager, FallbackStrategy


@pytest.mark.asyncio
async def test_fallback_cascade_to_degraded():
    fm = FallbackManager()

    def failing_primary():
        raise RuntimeError("Primary provider down")

    def failing_secondary():
        raise RuntimeError("Secondary model down")

    res = await fm.execute_with_fallback(
        primary_func=failing_primary,
        fallback_funcs=[failing_secondary],
    )

    assert res["is_degraded"] is True
    assert res["status"] == "degraded_success"
