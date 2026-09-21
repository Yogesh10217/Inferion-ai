"""
Tests for Agent MessageBus & Messaging Layer
"""

import pytest

from app.multi_agent.agent_messaging import AgentMessage, MessageBus, MessageType


@pytest.mark.asyncio
async def test_message_bus_publish_and_subscribe():
    bus = MessageBus()
    received_msgs = []

    def subscriber_cb(msg: AgentMessage):
        received_msgs.append(msg)

    bus.subscribe("agent_b", subscriber_cb)

    msg = AgentMessage(
        sender_id="agent_a",
        recipient_id="agent_b",
        message_type=MessageType.TASK,
        content="Execute task #1",
        team_id="team_test",
    )
    await bus.publish(msg)

    assert len(received_msgs) == 1
    assert received_msgs[0].content == "Execute task #1"

    history = bus.get_team_history("team_test")
    assert len(history) == 1
    assert history[0].sender_id == "agent_a"
