"""
Tests for Negotiation Engine
"""

import pytest
from app.multi_agent.agent_negotiation import NegotiationEngine


def test_negotiation_disagreement_resolution():
    engine = NegotiationEngine(max_rounds=3)
    proposals = {
        "agent_dev": "Use FastAPI REST API",
        "agent_qa": "Use GraphQL API",
    }
    outcome = engine.negotiate(proposals, arbitrator_id="lead_mgr")

    assert outcome.is_resolved is True
    assert outcome.rounds_conducted >= 1
    assert "Compromise proposal" in outcome.final_agreement
    assert outcome.arbitrated_by == "lead_mgr"
