"""Unit tests for Human Experience & Escalation."""

from app.application_platform.human_experience import (
    EscalationReason,
    HumanExperienceManager,
)
from app.orchestration.human_tasks import HumanTaskManager


def test_trigger_and_resolve_escalation():
    task_mgr = HumanTaskManager()
    hexp_mgr = HumanExperienceManager(human_task_manager=task_mgr)

    esc = hexp_mgr.trigger_escalation(
        tenant_id="t1",
        application_id="app_fin",
        execution_id="exec_999",
        reason=EscalationReason.HIGH_RISK,
        details="High financial transfer detected",
    )

    assert esc.status == "OPEN"
    assert esc.human_task_id is not None

    # Resolve escalation
    resolved = hexp_mgr.resolve_escalation(
        escalation_id=esc.escalation_id,
        resolution_notes="Approved by senior risk officer",
        approved=True,
    )

    assert resolved.status == "RESOLVED"
    assert resolved.resolution_notes == "Approved by senior risk officer"
