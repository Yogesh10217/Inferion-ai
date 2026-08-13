"""
Tests for Agent Framework (Phase 5.1) & Memory Integration
"""

from app.memory.memory_manager import MemoryManager


def test_agent_memory_prompt_assembly():
    mm = MemoryManager()
    mm.update_profile("agent_user", {"preferred_language": "python", "preferred_framework": "fastapi"})
    mm.service.semantic_tier.store_fact("User requires zero-mock production implementations")

    ctx = mm.assemble_context(user_id="agent_user", session_id="sess_agent", query="implementation rules")
    assert ctx.user_profile["preferred_framework"] == "fastapi"
    assert len(ctx.semantic_facts) >= 1
    assert "User requires zero-mock production implementations" in ctx.semantic_facts[0]["fact"]

    formatted = ctx.format_prompt_context()
    assert "User Profile" in formatted
    assert "Learned Facts" in formatted
