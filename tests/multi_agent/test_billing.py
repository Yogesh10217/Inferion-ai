"""
Tests for TeamBillingTracker Usage Accounting
"""

from app.multi_agent.agent_billing import TeamBillingTracker


def test_team_billing_tracker():
    tracker = TeamBillingTracker()
    tracker.track_run(
        team_id="team_dev_1",
        tenant_id="tenant_x",
        duration_seconds=5.2,
        cost=0.025,
        agent_costs={"agent_mgr": 0.005, "agent_dev": 0.02},
        tool_calls=3,
        api_calls=1,
    )

    summary = tracker.get_team_billing_summary("team_dev_1")
    assert summary["total_runs"] == 1
    assert summary["total_cost"] == 0.025
    assert summary["total_duration_seconds"] == 5.2
    assert summary["tool_calls"] == 3
    assert summary["agent_breakdown"]["agent_dev"] == 0.02
