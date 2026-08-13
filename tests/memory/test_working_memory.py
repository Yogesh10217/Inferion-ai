"""
Tests for Working Memory (Tier 1)
"""

from app.memory.working_memory import WorkingMemory


def test_working_memory_lifecycle():
    wm = WorkingMemory("exec_123")
    wm.put("planner_step", 1)
    wm.put("tool_result", {"status": "ok"})

    assert wm.get("planner_step") == 1
    assert wm.get("tool_result")["status"] == "ok"
    assert wm.get("missing", "default") == "default"

    snap = wm.snapshot()
    assert snap["planner_step"] == 1

    wm.clear()
    assert wm.get("planner_step") is None

    wm.restore(snap)
    assert wm.get("planner_step") == 1
    assert wm.remove("planner_step") is True
    assert wm.remove("planner_step") is False
