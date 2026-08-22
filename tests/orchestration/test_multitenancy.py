"""Unit tests for strict multi-tenant isolation in process definitions, executions, cases, and human tasks."""

import pytest
from app.orchestration.workflow import WorkflowDefinitionManager, WorkflowStep
from app.orchestration.execution import WorkflowExecutionEngine
from app.orchestration.human_tasks import HumanTaskManager
from app.orchestration.case_management import CaseManager


def test_orchestration_multi_tenancy():
    def_mgr = WorkflowDefinitionManager()
    exec_eng = WorkflowExecutionEngine()
    ht_mgr = HumanTaskManager()
    c_mgr = CaseManager()

    # Tenant A Setup
    wf_A = def_mgr.create_definition("WF A", steps=[WorkflowStep(step_id="s1", name="S1")], tenant_id="Tenant_A")
    exec_A = exec_eng.start_execution(wf_A, tenant_id="Tenant_A")
    ht_mgr.create_task("Task A", tenant_id="Tenant_A")
    c_mgr.create_case("Case A", tenant_id="Tenant_A")

    # Tenant B Setup
    wf_B = def_mgr.create_definition("WF B", steps=[WorkflowStep(step_id="s1", name="S1")], tenant_id="Tenant_B")
    exec_B = exec_eng.start_execution(wf_B, tenant_id="Tenant_B")
    ht_mgr.create_task("Task B", tenant_id="Tenant_B")
    c_mgr.create_case("Case B", tenant_id="Tenant_B")

    # Verify zero leakage across tenant boundaries
    assert len(def_mgr.list_definitions("Tenant_A")) == 1
    assert len(def_mgr.list_definitions("Tenant_B")) == 1
    assert len(exec_eng.list_executions("Tenant_A")) == 1
    assert len(exec_eng.list_executions("Tenant_B")) == 1
    assert len(ht_mgr.list_tasks("Tenant_A")) == 1
    assert len(c_mgr.list_cases("Tenant_A")) == 1
