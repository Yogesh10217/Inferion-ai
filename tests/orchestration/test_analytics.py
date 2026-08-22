"""Unit tests for ProcessAnalyticsEngine."""

import pytest
from app.orchestration.analytics import ProcessAnalyticsEngine


def test_process_insight_generation():
    engine = ProcessAnalyticsEngine()
    insight = engine.generate_insight("t_an")

    assert insight.tenant_id == "t_an"
    assert insight.automation_rate >= 90.0
    assert "human_approval_step" in insight.bottlenecks
