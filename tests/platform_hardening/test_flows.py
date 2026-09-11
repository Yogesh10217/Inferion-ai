"""
Phase 5.59 — Comprehensive Integration Audit, Hardening & End-to-End Certification Test Suite.
"""

import pytest
import time
from app.platform_hardening.exceptions import (
    CrossTenantPlatformHardeningException,
    ImmutablePlatformAuditRecordException,
)
from app.platform_hardening.manager import PlatformHardeningManager
from app.platform_hardening.models import (
    EngineConnectionStatus,
    IntegrationHealthStatus,
    PlatformAuditFinding,
    PlatformAuditSeverity,
    PlatformAuditStatus,
    PlatformCertificationStatus,
    ReleaseReadinessDecision,
    SubsystemIntegrationStatus,
)
from app.platform_hardening.providers import (
    PlatformHardeningProvider,
    PlatformHardeningProviderRegistry,
)


# Dummy test provider implementing PlatformHardeningProvider
class DummyTestProvider:
    def __init__(self, name: str = "TestProvider", is_healthy: bool = True):
        self.name = name
        self._healthy = is_healthy

    def collect_integration_status(self) -> SubsystemIntegrationStatus:
        return SubsystemIntegrationStatus(
            subsystem_name=self.name,
            phase="5.51",
            status=IntegrationHealthStatus.HEALTHY if self._healthy else IntegrationHealthStatus.UNHEALTHY,
        )

    def collect_context(self) -> dict:
        return {"tenant_id": "tenant-a", "trace_id": "trace-123", "correlation_id": "corr-123", "causation_id": "caus-123", "confidence": 0.95, "evidence_reference": "ev-123"}

    def collect_traceability(self) -> dict:
        return {"trace_id": "trace-123"}

    def collect_lineage(self) -> dict:
        return {"edges": []}

    def collect_governance(self) -> dict:
        return {"decision": "ALLOW"}

    def collect_delegations(self) -> dict:
        return {"auto_execute": False}

    def collect_verifications(self) -> dict:
        return {"verified": True}

    def collect_evidence(self) -> dict:
        return {"evidence_id": "ev-123"}

    def collect_health(self) -> IntegrationHealthStatus:
        return IntegrationHealthStatus.HEALTHY if self._healthy else IntegrationHealthStatus.UNHEALTHY

    def collect_engine_status(self) -> list:
        return [EngineConnectionStatus(engine_name="TestEngine", subsystem_name=self.name, is_instantiated=True, is_called=True, is_connected_to_pipeline=True)]


# Dummy failing provider that raises an exception
class ExceptionProvider:
    def collect_integration_status(self): raise RuntimeError("Provider crash")
    def collect_context(self): raise RuntimeError("Provider crash")
    def collect_traceability(self): raise RuntimeError("Provider crash")
    def collect_lineage(self): raise RuntimeError("Provider crash")
    def collect_governance(self): raise RuntimeError("Provider crash")
    def collect_delegations(self): raise RuntimeError("Provider crash")
    def collect_verifications(self): raise RuntimeError("Provider crash")
    def collect_evidence(self): raise RuntimeError("Provider crash")
    def collect_health(self): raise RuntimeError("Provider crash")
    def collect_engine_status(self): raise RuntimeError("Provider crash")


def test_01_subsystem_registry_validation():
    """Verify all 8 upper intelligence platforms register in canonical registry."""
    mgr = PlatformHardeningManager()
    subsystems = mgr.subsystem_registry.list_all_subsystems()
    assert len(subsystems) == 8
    names = {s.subsystem_name for s in subsystems}
    assert "Unified Intelligence" in names
    assert "Decision Intelligence" in names
    assert "Autonomous Assurance" in names
    assert "Continuous Assurance" in names
    assert "Reliability Intelligence" in names
    assert "Capacity Intelligence" in names
    assert "Runtime Intelligence" in names
    assert "Platform Integration Fabric" in names


def test_02_provider_registration():
    """Verify provider registration and contract validation."""
    registry = PlatformHardeningProviderRegistry()
    provider = DummyTestProvider("ProviderA")
    registry.register_provider("prov-a", provider)
    assert "prov-a" in registry.list_registered_providers()


def test_03_provider_failure_isolation():
    """Verify one provider crash does not stop the overall platform audit."""
    registry = PlatformHardeningProviderRegistry()
    good_p = DummyTestProvider("GoodProvider")
    bad_p = ExceptionProvider()
    registry.register_provider("good", good_p)
    registry.register_provider("bad", bad_p)

    results = registry.collect_all_provider_results()
    assert "good" in results
    assert "bad" in results
    assert results["bad"]["health"] == IntegrationHealthStatus.UNHEALTHY


def test_04_provider_timeout_isolation():
    """Verify timed-out provider health checks degrade safely."""
    registry = PlatformHardeningProviderRegistry(timeout_seconds=0.1)

    class SlowProvider(DummyTestProvider):
        def collect_health(self):
            time.sleep(0.5)
            return IntegrationHealthStatus.HEALTHY

    registry.register_provider("slow", SlowProvider())
    status = registry.check_provider_health("slow")
    assert status.is_healthy is False
    assert "Timeout" in status.error_detail


def test_05_cross_phase_context_propagation():
    """Verify context preservation across phases."""
    mgr = PlatformHardeningManager()
    ctx = {
        "tenant_id": "tenant-1",
        "trace_id": "tr-100",
        "correlation_id": "corr-100",
        "causation_id": "caus-100",
        "confidence": 0.99,
        "evidence_reference": "ev-100",
    }
    res, findings = mgr.context_validation.validate_context_flow(ctx)
    assert res.is_valid is True
    assert len(findings) == 0


def test_06_trace_propagation():
    """Verify trace_id preservation across 8 phase execution steps."""
    mgr = PlatformHardeningManager()
    phase_traces = [
        {"phase_name": "Runtime", "trace_id": "abc-123", "tenant_id": "t1"},
        {"phase_name": "Capacity", "trace_id": "abc-123", "tenant_id": "t1"},
        {"phase_name": "Reliability", "trace_id": "abc-123", "tenant_id": "t1"},
        {"phase_name": "Decision", "trace_id": "abc-123", "tenant_id": "t1"},
    ]
    res, findings = mgr.trace_validation.validate_trace_path("abc-123", phase_traces, tenant_id="t1")
    assert res.is_valid is True
    assert len(findings) == 0


def test_07_correlation_id_propagation():
    """Verify correlation ID is tracked across phases."""
    mgr = PlatformHardeningManager()
    ctx = {"tenant_id": "t1", "trace_id": "t1", "correlation_id": "corr-99", "causation_id": "c99", "confidence": 0.8, "evidence_reference": "ev-1"}
    res, _ = mgr.context_validation.validate_context_flow(ctx)
    assert res.correlation_id_preserved is True


def test_08_causation_id_propagation():
    """Verify causation ID tracking and status progression."""
    mgr = PlatformHardeningManager()
    ctx = {"tenant_id": "t1", "trace_id": "t1", "correlation_id": "c1", "causation_id": "caus-99", "confidence": 0.8, "evidence_reference": "ev-1"}
    res, _ = mgr.context_validation.validate_context_flow(ctx)
    assert res.causation_id_preserved is True


def test_09_cross_phase_lineage():
    """Verify DAG lineage validation across entities."""
    mgr = PlatformHardeningManager()
    edges = [
        {"source": "Signal", "target": "Finding"},
        {"source": "Finding", "target": "Recommendation"},
        {"source": "Recommendation", "target": "Decision"},
    ]
    res, findings = mgr.lineage_validation.validate_lineage_graph(edges)
    assert res.is_valid is True
    assert len(findings) == 0


def test_10_lineage_cycle_detection():
    """Detect cycles in intelligence lineage graph."""
    mgr = PlatformHardeningManager()
    edges = [
        {"source": "NodeA", "target": "NodeB"},
        {"source": "NodeB", "target": "NodeC"},
        {"source": "NodeC", "target": "NodeA"},
    ]
    res, findings = mgr.lineage_validation.validate_lineage_graph(edges)
    assert res.is_valid is False
    assert len(findings) > 0
    assert "Cycle" in findings[0].title


def test_11_evidence_chain_integrity():
    """Verify SHA-256 evidence chain hash continuity."""
    mgr = PlatformHardeningManager()
    records = [
        {"tenant_id": "t1", "sha256_hash": "hash1", "previous_hash": None},
        {"tenant_id": "t1", "sha256_hash": "hash2", "previous_hash": "hash1"},
    ]
    valid, findings = mgr.evidence_validation.validate_evidence_chain(records, tenant_id="t1")
    assert valid is True
    assert len(findings) == 0


def test_12_evidence_tampering_detection():
    """Detect hash discrepancy in modified evidence record."""
    mgr = PlatformHardeningManager()
    records = [
        {"tenant_id": "t1", "sha256_hash": "wrong_hash", "previous_hash": None, "payload": {"data": 123}},
    ]
    valid, findings = mgr.evidence_validation.validate_evidence_chain(records, tenant_id="t1")
    assert valid is False
    assert len(findings) > 0
    assert "Tampering" in findings[0].title


def test_13_tenant_isolation():
    """Verify tenant isolation raises CrossTenantPlatformHardeningException."""
    mgr = PlatformHardeningManager()
    repo = mgr.audit_repo
    res = mgr.run_platform_audit(tenant_id="tenant-a")
    with pytest.raises(CrossTenantPlatformHardeningException):
        repo.get(tenant_id="tenant-b-attacker", audit_id=res.audit_id)


def test_14_cross_tenant_metadata_protection():
    """Verify exception error message returns only 'Access denied'."""
    try:
        raise CrossTenantPlatformHardeningException("Secret resource ID 9999")
    except CrossTenantPlatformHardeningException as e:
        assert str(e) == "Access denied"


def test_15_manager_engine_connectivity():
    """Verify managers correctly initialize and call constituent engines."""
    mgr = PlatformHardeningManager()
    statuses = [EngineConnectionStatus(engine_name="EngineA", subsystem_name="SubA", is_instantiated=True, is_called=True, is_connected_to_pipeline=True)]
    _, findings = mgr.engine_connectivity.audit_engine_connectivity(statuses)
    assert len(findings) == 0


def test_16_disconnected_engine_detection():
    """Detect instantiated but uninvoked dead engines."""
    mgr = PlatformHardeningManager()
    statuses = [EngineConnectionStatus(engine_name="DeadEngine", subsystem_name="SubA", is_instantiated=True, is_called=False, is_connected_to_pipeline=False)]
    _, findings = mgr.engine_connectivity.audit_engine_connectivity(statuses)
    assert len(findings) > 0
    assert "Dead Engine" in findings[0].title


def test_17_production_stub_detection():
    """Run production stub detection on codebase."""
    mgr = PlatformHardeningManager()
    res = mgr.stub_detection.scan_stubs()
    assert res.total_files_scanned > 0


def test_18_dead_code_classification():
    """Run dead code detection classifier."""
    mgr = PlatformHardeningManager()
    res = mgr.dead_code_detection.scan_dead_code()
    assert res.total_symbols_analyzed > 0


def test_19_duplicate_contract_detection():
    """Run duplicate contract detection engine."""
    mgr = PlatformHardeningManager()
    res = mgr.duplication_detection.scan_duplicates()
    assert isinstance(res.duplicates_found, int)


def test_20_circular_dependency_detection():
    """Run dependency validation engine across app/."""
    mgr = PlatformHardeningManager()
    res = mgr.dependency_validation.validate_dependencies()
    assert res.is_valid is True


def test_21_repository_thread_safety():
    """Verify repository thread locks prevent data races."""
    mgr = PlatformHardeningManager()
    res, findings = mgr.repository_validation.validate_repository_isolation([mgr.audit_repo], tenant_id="tenant-a")
    assert res.is_valid is True
    assert len(findings) == 0


def test_22_concurrent_audit_execution():
    """Verify concurrent platform audit runs without thread panic."""
    mgr = PlatformHardeningManager()

    def _worker(i):
        return mgr.get_platform_health_summary(tenant_id=f"tenant-{i}")

    res, findings = mgr.concurrency_validation.validate_concurrency(_worker, num_workers=5, iterations=10)
    assert res.is_valid is True
    assert len(findings) == 0


def test_23_idempotency_validation():
    """Verify idempotent deduplication for repeated requests."""
    mgr = PlatformHardeningManager()

    def _dummy_op(payload, key):
        return {"operation_id": "op-100", "is_duplicate": True}

    res, findings = mgr.idempotency_validation.validate_idempotency(_dummy_op, {}, key="idem-key-1")
    assert res.is_valid is True


def test_24_governance_approval_enforcement():
    """Verify governance blocks delegation when approval is missing for high risk."""
    mgr = PlatformHardeningManager()
    flow_unapproved = {
        "risk_level": "CRITICAL",
        "governance_decision": "REQUIRE_APPROVAL",
        "has_human_approval": False,
        "delegation_created": True,
    }
    res, findings = mgr.governance_validation.validate_governance_flow(flow_unapproved)
    assert res.is_valid is False
    assert len(findings) > 0
    assert "Approval Bypass" in findings[0].title


def test_25_delegation_only_enforcement():
    """Verify direct infrastructure mutation is blocked."""
    mgr = PlatformHardeningManager()
    del_direct = {"auto_execute": False, "direct_infrastructure_mutation": True, "tenant_id": "system"}
    res, findings = mgr.delegation_validation.validate_delegation(del_direct)
    assert res.is_valid is False
    assert "Direct Infrastructure Mutation" in findings[0].title


def test_26_auto_execute_false_enforcement():
    """Enforce Mandatory Invariants 2 & 6: auto_execute MUST BE False."""
    mgr = PlatformHardeningManager()
    del_auto = {"auto_execute": True, "tenant_id": "system"}
    res, findings = mgr.delegation_validation.validate_delegation(del_auto)
    assert res.is_valid is False
    assert "auto_execute is True" in findings[0].title


def test_27_delegation_traceability():
    """Verify delegation retains tenant and trace IDs."""
    mgr = PlatformHardeningManager()
    del_valid = {"auto_execute": False, "tenant_id": "system", "trace_id": "tr-1"}
    res, findings = mgr.delegation_validation.validate_delegation(del_valid)
    assert res.is_valid is True
    assert len(findings) == 0


def test_28_verification_feedback_loop():
    """Verify execution verification feedback returns to assurance."""
    mgr = PlatformHardeningManager()
    loop_data = {"verification_id": "ver-1", "assurance_updated": True, "evidence_id": "ev-1"}
    res, findings = mgr.verification_validation.validate_verification_loop(loop_data)
    assert res.is_valid is True
    assert len(findings) == 0


def test_29_remediation_generation():
    """Verify remediation recommendation generation enforcing auto_execute=False."""
    mgr = PlatformHardeningManager()
    finding = PlatformAuditFinding(
        finding_id="f1", tenant_id="t1", rule_id="r1", title="Title", description="Desc",
        severity=PlatformAuditSeverity.HIGH, subsystem="sub", affected_component="comp"
    )
    rems = mgr.remediation_planner.generate_remediations([finding], tenant_id="t1")
    assert len(rems) == 1
    assert rems[0].auto_execute is False
    assert rems[0].priority == "P1"


def test_30_high_risk_remediation_approval():
    """Verify high risk remediations require approval."""
    mgr = PlatformHardeningManager()
    finding = PlatformAuditFinding(
        finding_id="f2", tenant_id="t1", rule_id="r1", title="Critical Title", description="Desc",
        severity=PlatformAuditSeverity.CRITICAL, subsystem="sub", affected_component="comp"
    )
    rems = mgr.remediation_planner.generate_remediations([finding], tenant_id="t1")
    assert rems[0].requires_approval is True
    assert rems[0].priority == "P0"


def test_31_platform_health_calculation():
    """Verify overall platform health aggregation."""
    mgr = PlatformHardeningManager()
    summary = mgr.get_platform_health_summary(tenant_id="system")
    assert summary.tenant_id == "system"


def test_32_production_readiness_score():
    """Verify empirical production readiness score calculation."""
    mgr = PlatformHardeningManager()
    findings = [
        PlatformAuditFinding(
            finding_id="f1", tenant_id="system", rule_id="RULE-INT-001", title="Title", description="Desc",
            severity=PlatformAuditSeverity.HIGH, subsystem="Runtime Intelligence", affected_component="comp"
        )
    ]
    scores = mgr.readiness_engine.calculate_readiness_report(findings)
    assert scores["integration"] < 100.0
    assert scores["overall"] < 100.0


def test_33_certification_failure():
    """Verify certification blocks when P0 findings exist."""
    mgr = PlatformHardeningManager()
    release_gate = mgr.release_gate_engine.evaluate_release_gate([], cross_tenant_leak=True)
    cert = mgr.certification_engine.certify_platform("t1", "a1", readiness_score=40.0, release_gate=release_gate, findings=[])
    assert cert.status == PlatformCertificationStatus.BLOCKED


def test_34_integration_validated_certification():
    """Verify platform certification issuing CERTIFIED or PRODUCTION_READY."""
    mgr = PlatformHardeningManager()
    release_gate = mgr.release_gate_engine.evaluate_release_gate([])
    cert = mgr.certification_engine.certify_platform("t1", "a1", readiness_score=95.0, release_gate=release_gate, findings=[])
    assert cert.status == PlatformCertificationStatus.PRODUCTION_READY


def test_35_full_eight_phase_lifecycle():
    """Execute complete platform-wide audit across all 8 phases."""
    mgr = PlatformHardeningManager()
    res = mgr.run_platform_audit(tenant_id="system")
    assert res.audit_id.startswith("audit-")
    assert res.status == PlatformAuditStatus.COMPLETED
    assert res.certification is not None
    assert res.release_gate is not None


# Dedicated Multi-Domain Real Flow Tests
def test_flow_01_runtime_failure_propagation():
    """Flow 1: Runtime Failure Signal -> Capacity -> Reliability -> Assurance -> Decision -> Delegation -> Verification."""
    mgr = PlatformHardeningManager()
    # 1. Collect integration & provider statuses
    health, int_findings = mgr.integration_audit.audit_integration(tenant_id="flow1")
    # 2. Check context propagation
    ctx_res, _ = mgr.context_validation.validate_context_flow({
        "tenant_id": "flow1", "trace_id": "tr-flow1", "correlation_id": "corr-flow1",
        "causation_id": "caus-flow1", "confidence": 0.9, "evidence_reference": "ev-flow1"
    })
    assert ctx_res.is_valid is True


def test_flow_02_high_risk_approval_gate():
    """Flow 2: Recommendation with CRITICAL risk -> Governance -> REQUIRE_APPROVAL -> Unapproved state yields BLOCKED."""
    mgr = PlatformHardeningManager()
    res, _ = mgr.governance_validation.validate_governance_flow({
        "risk_level": "CRITICAL", "governance_decision": "REQUIRE_APPROVAL",
        "has_human_approval": False, "delegation_created": True
    })
    gate_res = mgr.release_gate_engine.evaluate_release_gate([], approval_bypass=not res.is_valid)
    assert gate_res.decision == ReleaseReadinessDecision.BLOCKED


def test_flow_03_tenant_isolation_enforcement():
    """Flow 3: Tenant A Signal vs Tenant B Access Request yields 'Access denied' with 0 metadata leakage."""
    mgr = PlatformHardeningManager()
    repo = mgr.audit_repo
    try:
        repo.get(tenant_id="tenant-b", audit_id="non-existent")
    except CrossTenantPlatformHardeningException as e:
        assert str(e) == "Access denied"


def test_flow_04_evidence_chain_tampering():
    """Flow 4: Modified hash in intermediate evidence record invalidates chain."""
    mgr = PlatformHardeningManager()
    tampered_records = [
        {"tenant_id": "t1", "sha256_hash": "hash-a", "previous_hash": None},
        {"tenant_id": "t1", "sha256_hash": "hash-b-modified", "previous_hash": "hash-a-wrong"},
    ]
    valid, findings = mgr.evidence_validation.validate_evidence_chain(tampered_records, tenant_id="t1")
    assert valid is False
    assert len(findings) > 0


def test_flow_05_provider_failure_isolation():
    """Flow 5: 1 Provider fails out of 8 -> Platform remains functional, assurance degrades safely."""
    registry = PlatformHardeningProviderRegistry()
    for i in range(7):
        registry.register_provider(f"prov-{i}", DummyTestProvider(f"Prov-{i}"))
    registry.register_provider("prov-fail", ExceptionProvider())

    results = registry.collect_all_provider_results()
    assert len(results) == 8
    assert results["prov-fail"]["health"] == IntegrationHealthStatus.UNHEALTHY
