"""
Tests for Consensus Engine
"""

import pytest
from app.multi_agent.agent_consensus import ConsensusEngine, ConsensusStrategy


def test_majority_vote_consensus():
    votes = {
        "agent_1": "option_A",
        "agent_2": "option_A",
        "agent_3": "option_B",
    }
    res = ConsensusEngine.evaluate_consensus(votes, strategy=ConsensusStrategy.MAJORITY_VOTE)
    assert res.decision == "option_A"
    assert res.is_agreed is True
    assert res.confidence_score == pytest.approx(2 / 3)


def test_unanimous_consensus_failure():
    votes = {
        "agent_1": "option_A",
        "agent_2": "option_B",
    }
    res = ConsensusEngine.evaluate_consensus(votes, strategy=ConsensusStrategy.UNANIMOUS_APPROVAL)
    assert res.is_agreed is False
