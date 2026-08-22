"""Unit tests for CaseManager case creation and timeline events."""

import pytest
from app.orchestration.case_management import CaseManager, CaseType, CaseStatus


def test_case_management_lifecycle():
    mgr = CaseManager()

    case = mgr.create_case("Vendor Onboarding Case", case_type=CaseType.CUSTOMER_ONBOARDING, tenant_id="t_case")
    assert case.status == CaseStatus.NEW
    assert len(case.timeline) == 1  # CASE_CREATED event

    upd_case = mgr.update_status(case.case_id, CaseStatus.IN_PROGRESS, reason="Review started")
    assert upd_case.status == CaseStatus.IN_PROGRESS
    assert len(case.timeline) == 2
