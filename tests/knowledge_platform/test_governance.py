"""Unit tests for KnowledgeGovernanceEngine policy decisions."""

import pytest
from app.knowledge_platform.governance import KnowledgeGovernanceEngine, PolicyDecisionType


def test_knowledge_governance_policy_eval():
    ge = KnowledgeGovernanceEngine()

    # Restricted + viewer -> BLOCK
    dec_block = ge.evaluate_access("user_guest", user_role="viewer", classification="RESTRICTED")
    assert dec_block.policy_decision == PolicyDecisionType.BLOCK

    # Secret -> REQUIRE_APPROVAL
    dec_appr = ge.evaluate_access("user_bob", user_role="admin", classification="SECRET")
    assert dec_appr.policy_decision == PolicyDecisionType.REQUIRE_APPROVAL
    assert dec_appr.approval_request_id is not None
