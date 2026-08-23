"""Unit tests for Decision Engine & Reproducible Snapshot Persistence."""

import pytest
from app.intelligence_platform.decisions import DecisionManager, DecisionOption, DecisionCriteria, DecisionStatus, DecisionSnapshot


def test_decision_reproducible_snapshot():
    mgr = DecisionManager()
    snap = DecisionSnapshot(
        signal_versions=["sig_1", "sig_2"],
        trust_score=88.5,
        policy_version="v2.1.0",
    )

    opt = DecisionOption(title="Option Rollback", action_type="ROLLBACK", target_resource_id="svc_1", is_selected=True)
    dec = mgr.create_decision("t1", title="Production Decision", options=[opt], snapshot=snap)

    assert dec.decision_id.startswith("dec_")
    assert dec.snapshot.trust_score == 88.5
    assert dec.snapshot.policy_version == "v2.1.0"
    assert dec.selected_option.title == "Option Rollback"
