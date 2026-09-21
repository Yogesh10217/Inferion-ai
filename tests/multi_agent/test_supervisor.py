"""
Tests for Supervisor Agent
"""

from app.multi_agent.agent_messaging import AgentMessage, MessageType
from app.multi_agent.agent_supervisor import SupervisorAgent


def test_supervisor_failure_monitoring():
    sup = SupervisorAgent()
    step_fail = {"status": "failed", "error": "Database connection lost"}
    ok = sup.monitor_execution_step(step_fail)

    assert ok is False
    assert len(sup.monitored_failures) == 1


def test_supervisor_deadlock_detection():
    sup = SupervisorAgent()
    msgs = [
        AgentMessage(sender_id=f"a_{i}", recipient_id="b", message_type=MessageType.QUESTION, content="?")
        for i in range(6)
    ]

    deadlocked = sup.detect_deadlock(msgs)
    assert deadlocked is True
