"""Mandatory End-to-End Test Suite for Phase 5.26 Enterprise AI Architecture Platform."""

import pytest

from app.architecture_platform.change_management import ArchitectureChangeStatus, ArchitectureChangeType
from app.architecture_platform.decisions import ArchitectureDecisionOption, ArchitectureDecisionStatus
from app.architecture_platform.dependencies import DependencyType
from app.architecture_platform.digital_twin import TwinSynchronizationStatus
from app.architecture_platform.exceptions import (
    CrossTenantArchitectureAccessException,
    ImmutableArchitectureDecisionException,
)
from app.architecture_platform.manager import ArchitecturePlatformManager
from app.architecture_platform.nodes import ArchitectureNodeType


@pytest.fixture
def arch_mgr():
    """Instantiate a clean ArchitecturePlatformManager for tests."""
    return ArchitecturePlatformManager()


def test_flow_1_architecture_discovery(arch_mgr):
    """Flow 1: Register Application -> Agent -> Workflow -> Data Asset -> Topology -> Dependencies."""
    tenant_id = "tenant_discovery"

    # Register nodes
    app_node = arch_mgr.discover_and_register_node(tenant_id, "Customer Portal", ArchitectureNodeType.APPLICATION)
    agent_node = arch_mgr.discover_and_register_node(tenant_id, "Support Agent", ArchitectureNodeType.AGENT)
    wf_node = arch_mgr.discover_and_register_node(tenant_id, "Ticket Workflow", ArchitectureNodeType.WORKFLOW)
    data_node = arch_mgr.discover_and_register_node(tenant_id, "User DB", ArchitectureNodeType.DATABASE)

    # Add dependencies
    arch_mgr.add_dependency(tenant_id, app_node.node_id, agent_node.node_id, DependencyType.CALLS)
    arch_mgr.add_dependency(tenant_id, agent_node.node_id, wf_node.node_id, DependencyType.ORCHESTRATES)
    arch_mgr.add_dependency(tenant_id, wf_node.node_id, data_node.node_id, DependencyType.READS)

    # Build & Verify Topology
    topology = arch_mgr.topology_manager.build_topology(tenant_id)
    assert len(topology.nodes) == 4
    assert app_node.node_id in topology.nodes
    assert len(arch_mgr.dependency_manager.list_dependencies(tenant_id)) == 3


def test_flow_2_change_impact(arch_mgr):
    """Flow 2: Model Replacement Proposal -> Blast Radius -> Simulation -> Risk -> Approval Requirement."""
    tenant_id = "tenant_impact"

    model_node = arch_mgr.discover_and_register_node(tenant_id, "Legacy LLM", ArchitectureNodeType.MODEL)
    agent_node = arch_mgr.discover_and_register_node(tenant_id, "Sales Bot", ArchitectureNodeType.AGENT)
    app_node = arch_mgr.discover_and_register_node(tenant_id, "Sales App", ArchitectureNodeType.APPLICATION)

    arch_mgr.add_dependency(tenant_id, agent_node.node_id, model_node.node_id, DependencyType.USES)
    arch_mgr.add_dependency(tenant_id, app_node.node_id, agent_node.node_id, DependencyType.CALLS)

    res = arch_mgr.propose_and_evaluate_change(
        tenant_id=tenant_id,
        idempotency_key="change_key_001",
        action_type=ArchitectureChangeType.REPLACE,
        target_node_ids=[model_node.node_id],
    )

    assert res["change"]["status"] in (
        ArchitectureChangeStatus.DRAFT.value,
        ArchitectureChangeStatus.APPROVED.value,
        ArchitectureChangeStatus.REQUIRES_APPROVAL.value,
    )
    assert res["impact_analysis"]["blast_radius"]["total_affected_count"] >= 1
    assert res["simulation"]["confidence_score"] > 80.0


def test_flow_3_architecture_drift(arch_mgr):
    """Flow 3: Snapshot -> Introduce Drift -> Detect Drift -> Audit Record."""
    tenant_id = "tenant_drift"

    arch_mgr.discover_and_register_node(tenant_id, "Auth Service", ArchitectureNodeType.SERVICE)
    snapshot = arch_mgr.topology_manager.create_snapshot(tenant_id, description="Baseline")

    # Introduce unauthorized node
    unauthorized = arch_mgr.discover_and_register_node(tenant_id, "Rogue Proxy", ArchitectureNodeType.EXTERNAL_SYSTEM)

    drifts = arch_mgr.drift_detector.detect_drift(tenant_id, snapshot.snapshot_id)
    assert len(drifts) >= 1
    assert drifts[0].affected_nodes[0] == unauthorized.node_id
    assert drifts[0].audit_reference is not None


def test_flow_4_cross_tenant_isolation(arch_mgr):
    """Flow 4: Cross-Tenant Isolation enforcement with zero metadata leakage."""
    tenant_a = "tenant_alpha"
    tenant_b = "tenant_beta"

    node_a = arch_mgr.discover_and_register_node(tenant_a, "Secret Alpha Core", ArchitectureNodeType.SERVICE)
    snap_a = arch_mgr.topology_manager.create_snapshot(tenant_a)

    # Attempt access from Tenant B -> BLOCK
    with pytest.raises(CrossTenantArchitectureAccessException):
        arch_mgr.node_manager.get_node(node_a.node_id, tenant_id=tenant_b)

    with pytest.raises(CrossTenantArchitectureAccessException):
        arch_mgr.topology_manager.get_snapshot(snap_a.snapshot_id, tenant_id=tenant_b)


def test_flow_5_resilience(arch_mgr):
    """Flow 5: Detect Single Point of Failure (SPOF) -> Concentration -> Recommendation -> Delegation."""
    tenant_id = "tenant_resilience"

    spof_db = arch_mgr.discover_and_register_node(tenant_id, "Central DB", ArchitectureNodeType.DATABASE)

    # 4 services dependent on Central DB
    for i in range(4):
        svc = arch_mgr.discover_and_register_node(tenant_id, f"Service {i}", ArchitectureNodeType.SERVICE)
        arch_mgr.add_dependency(tenant_id, svc.node_id, spof_db.node_id, DependencyType.READS)

    res_eval = arch_mgr.resilience_analyzer.evaluate_resilience(tenant_id)
    assert len(res_eval.spofs) >= 1
    assert res_eval.spofs[0].node_id == spof_db.node_id
    assert len(res_eval.recommendations) >= 1


def test_flow_6_digital_twin(arch_mgr):
    """Flow 6: Digital Twin Synchronization & Drift Detection."""
    tenant_id = "tenant_twin"

    arch_mgr.discover_and_register_node(tenant_id, "API Gateway", ArchitectureNodeType.API)
    arch_mgr.topology_manager.create_snapshot(tenant_id)

    twin = arch_mgr.digital_twin_manager.synchronize_twin(
        tenant_id=tenant_id,
        operational_state_ref="HEALTHY",
        cost_usd=120.0,
        risk_level="LOW",
    )

    assert twin.state.sync_status == TwinSynchronizationStatus.OBSERVED

    drift_report = arch_mgr.digital_twin_manager.detect_twin_drift(tenant_id)
    assert drift_report["has_twin_drift"] is False


def test_flow_7_immutable_architecture_decision(arch_mgr):
    """Flow 7: Architecture Decision Record (ADR) creation, finalization, and immutability."""
    tenant_id = "tenant_adr"

    opt1 = ArchitectureDecisionOption(title="Use Postgres", description="Relational DB")
    opt2 = ArchitectureDecisionOption(title="Use Mongo", description="Document DB")

    adr = arch_mgr.decision_manager.create_adr(tenant_id, "Database Standard", "Selecting DB", [opt1, opt2])
    finalized = arch_mgr.decision_manager.finalize_adr(
        adr.decision_id, tenant_id, opt1.option_id, "ACID Compliance required"
    )

    assert finalized.status == ArchitectureDecisionStatus.FINALIZED

    # Attempt modification on finalized ADR -> BLOCK
    with pytest.raises(ImmutableArchitectureDecisionException):
        arch_mgr.decision_manager.update_draft_adr(adr.decision_id, tenant_id, title="Attempt Mutation")


def test_flow_8_high_risk_change(arch_mgr):
    """Flow 8: High-Risk Change Proposal -> Approval -> Delegation -> Verification."""
    tenant_id = "tenant_high_risk"

    # Create interconnected nodes to trigger High Risk
    target = arch_mgr.discover_and_register_node(tenant_id, "Core Auth Engine", ArchitectureNodeType.SERVICE)
    for i in range(6):
        c = arch_mgr.discover_and_register_node(tenant_id, f"Client {i}", ArchitectureNodeType.APPLICATION)
        arch_mgr.add_dependency(tenant_id, c.node_id, target.node_id, DependencyType.CALLS)

    eval_res = arch_mgr.propose_and_evaluate_change(
        tenant_id=tenant_id,
        idempotency_key="high_risk_key_100",
        action_type=ArchitectureChangeType.REMOVE,
        target_node_ids=[target.node_id],
    )

    change = eval_res["change"]
    assert change["status"] == ArchitectureChangeStatus.REQUIRES_APPROVAL.value

    # Approve approval request via approval engine
    app_id = change["approval_request_id"]
    arch_mgr.governance_engine.approval_engine.approve(app_id, approver_id="sec_admin")
    arch_mgr.change_manager.update_status(change["change_id"], tenant_id, ArchitectureChangeStatus.APPROVED)

    # Delegate execution
    del_change = arch_mgr.delegate_approved_change(
        change["change_id"], tenant_id, delegated_subsystem="PlatformOperationsManager"
    )
    assert del_change.status == ArchitectureChangeStatus.VERIFIED


def test_flow_9_secret_redaction(arch_mgr):
    """Flow 9: Secret Sanitization across node attributes and telemetry."""
    tenant_id = "tenant_secrets"

    attributes = {
        "db_port": 5432,
        "db_password": "SuperSecretPassword123!",
        "api_key": "sk_live_99999",
    }

    node = arch_mgr.discover_and_register_node(
        tenant_id,
        "Secure Storage Node",
        ArchitectureNodeType.DATABASE,
        attributes=attributes,
    )

    assert node.metadata.attributes["db_port"] == 5432
    assert node.metadata.attributes["db_password"] == "[REDACTED]"
    assert node.metadata.attributes["api_key"] == "[REDACTED]"


def test_flow_10_full_architecture_lifecycle(arch_mgr):
    """Flow 10: Complete Architecture Lifecycle from Discovery to Final Verification."""
    tenant_id = "tenant_full_lifecycle"

    # 1. Discover
    svc = arch_mgr.discover_and_register_node(tenant_id, "Order Service", ArchitectureNodeType.SERVICE)
    db = arch_mgr.discover_and_register_node(tenant_id, "Order DB", ArchitectureNodeType.DATABASE)
    arch_mgr.add_dependency(tenant_id, svc.node_id, db.node_id, DependencyType.READS)

    # 2. Topology & Snapshot
    snap = arch_mgr.topology_manager.create_snapshot(tenant_id, description="Initial Baseline")
    assert snap.is_finalized is True

    # 3. Change Proposal & Impact
    eval_res = arch_mgr.propose_and_evaluate_change(
        tenant_id=tenant_id,
        idempotency_key="lifecycle_key_999",
        action_type=ArchitectureChangeType.MODIFY,
        target_node_ids=[svc.node_id],
    )
    assert eval_res["impact_analysis"]["confidence_score"] > 80.0

    # 4. Delegation & Verification
    change_id = eval_res["change"]["change_id"]
    arch_mgr.change_manager.update_status(change_id, tenant_id, ArchitectureChangeStatus.APPROVED)
    verified_change = arch_mgr.delegate_approved_change(change_id, tenant_id)
    assert verified_change.status == ArchitectureChangeStatus.VERIFIED

    # 5. Analytics
    report = arch_mgr.analytics_engine.generate_report(tenant_id)
    assert report.total_nodes_count == 2
    assert report.total_dependencies_count == 1
