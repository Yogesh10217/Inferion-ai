"""Unit tests for DataGovernanceEngine and approval gating."""

import pytest
from app.data_fabric.governance import DataGovernanceEngine, DataClassification
from app.data_fabric.exceptions import DataAccessDenied


def test_data_governance_policy_evaluation():
    engine = DataGovernanceEngine()

    # Internal data access is permitted
    decision = engine.evaluate_access(
        tenant_id="t1",
        resource_id="res_internal",
        classification=DataClassification.INTERNAL,
        requester_id="agent_1",
    )
    assert decision.permitted is True

    # High-risk PII classification requires approval
    decision_pii = engine.evaluate_access(
        tenant_id="t1",
        resource_id="res_pii",
        classification=DataClassification.PII,
        requester_id="agent_1",
    )
    assert decision_pii.permitted is False
    assert decision_pii.requires_approval is True
    assert decision_pii.approval_request_id is not None
