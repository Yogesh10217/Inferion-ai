"""Unit tests for Feedback & Improvement Recommendations."""

import pytest
from app.application_platform.feedback import FeedbackManager, FeedbackType


def test_submit_feedback_generates_recommendation():
    mgr = FeedbackManager()

    fb = mgr.submit_feedback(
        tenant_id="t1",
        application_id="app_1",
        execution_id="exec_1",
        feedback_type=FeedbackType.CORRECTION,
        corrected_output="Use formal tone when speaking to enterprise customers.",
    )

    assert fb.signal.feedback_type == FeedbackType.CORRECTION
    
    recs = mgr.list_recommendations("t1", "app_1")
    assert len(recs) == 1
    assert recs[0].requires_approval is True
    assert recs[0].approved_by_governance is False
