"""Unit tests for Idempotent Actionable Recommendation Engine."""

import pytest

from app.intelligence_platform.exceptions import RecommendationStaleException
from app.intelligence_platform.recommendations import RecommendationManager, RecommendationStatus, RecommendationType


def test_recommendation_idempotency_and_superseding():
    mgr = RecommendationManager()
    rec1 = mgr.create_recommendation(
        "t1",
        RecommendationType.ROLLBACK_DEPLOYMENT,
        "Rollback Deploy",
        "Rollback action",
        "svc_1",
        "Risk reduction",
        idempotency_key="key_123",
    )

    # Idempotent call returns original recommendation
    rec1_dup = mgr.create_recommendation(
        "t1",
        RecommendationType.ROLLBACK_DEPLOYMENT,
        "Rollback Deploy",
        "Rollback action",
        "svc_1",
        "Risk reduction",
        idempotency_key="key_123",
    )
    assert rec1_dup.recommendation_id == rec1.recommendation_id

    # Create new recommendation and supersede old one
    rec2 = mgr.create_recommendation(
        "t1",
        RecommendationType.SCALE_RESOURCE,
        "Scale Deploy",
        "Scale action",
        "svc_1",
        "Performance boost",
        idempotency_key="key_456",
    )
    mgr.supersede_recommendation(rec1.recommendation_id, rec2.recommendation_id, "t1")

    assert mgr.get_recommendation(rec1.recommendation_id, "t1").status == RecommendationStatus.SUPERSEDED

    # Updating status on superseded recommendation raises RecommendationStaleException
    with pytest.raises(RecommendationStaleException):
        mgr.update_status(rec1.recommendation_id, "t1", RecommendationStatus.EXECUTING)
