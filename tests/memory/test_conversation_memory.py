"""
Tests for Conversation Memory (Tier 2)
"""

from app.memory.conversation_memory import ConversationMemory


def test_conversation_memory_append_and_trim():
    cm = ConversationMemory(session_id="sess_123", max_messages=3)
    cm.append_message("user", "Hello 1")
    cm.append_message("assistant", "Hi 1")
    cm.append_message("user", "Hello 2")

    assert len(cm.messages) == 3

    # Add 4th message -> should trim oldest
    cm.append_message("assistant", "Hi 2")
    assert len(cm.messages) == 3
    assert cm.messages[0]["content"] == "Hi 1"
    assert cm.summary is not None

    ctx = cm.retrieve_context()
    assert ctx["session_id"] == "sess_123"
    assert len(ctx["messages"]) == 3


def test_conversation_memory_compress():
    cm = ConversationMemory(session_id="sess_456")
    cm.append_message("user", "What is FastAPI?")
    cm.append_message("assistant", "FastAPI is a Python web framework.")

    comp = cm.compress()
    assert "Conversation summary" in comp["summary"]
    assert cm.summarize() != ""
