"""Unit tests for Application Resilience & Graceful Degradation."""

import pytest
from app.application_platform.resilience import (
    ApplicationResilienceManager,
    DegradationStrategy,
)


def test_graceful_degradation_target_resolution():
    mgr = ApplicationResilienceManager()

    mgr.register_fallback(
        tenant_id="t1",
        application_id="app_1",
        primary_target="gpt-4o",
        fallback_target="gpt-4o-mini",
        strategy=DegradationStrategy.MODEL_FALLBACK,
    )

    # Primary healthy -> Primary model returned
    res_normal = mgr.resolve_target("t1", "app_1", "gpt-4o", primary_failed=False)
    assert res_normal["target"] == "gpt-4o"
    assert res_normal["is_fallback"] is False

    # Primary failed -> Fallback model returned
    res_fallback = mgr.resolve_target("t1", "app_1", "gpt-4o", primary_failed=True)
    assert res_fallback["target"] == "gpt-4o-mini"
    assert res_fallback["is_fallback"] is True
    assert res_fallback["strategy"] == "MODEL_FALLBACK"
