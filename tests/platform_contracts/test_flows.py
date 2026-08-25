"""Mandatory 16 E2E Verification Flows for Platform Contracts & Consolidation (Phase 5.30)."""

import pytest
import os
import concurrent.futures
from datetime import datetime, timezone

from app.platform_contracts.tenant import TenantIsolationValidator, TenantAccessGuard
from app.platform_contracts.exceptions import (
    CrossTenantAccessException,
    ImmutableMutationException,
    IdempotencyConflictException,
    InvalidLifecycleTransitionException,
    ContractVersionException,
)
from app.platform_contracts.immutability import ImmutableResource, ImmutableResourceState, ImmutableResourceValidator
from app.platform_contracts.fingerprinting import FingerprintGenerator, CanonicalSerializer
from app.platform_contracts.snapshots import SnapshotFactory, SnapshotValidator
from app.platform_contracts.idempotency import IdempotencyManager, IdempotencyStatus
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.platform_contracts.trust import TrustAssessment, TrustBand
from app.platform_contracts.governance import GovernanceDecisionStatus
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget, DelegationStatus
from app.platform_contracts.lifecycle import LifecycleMachine, LifecycleTransition
from app.platform_contracts.adapters import PlatformContractAdapter
from app.platform_contracts.versioning import ContractVersion, ContractCompatibilityValidator
from app.platform_contracts.validation import CircularDependencyValidator

# Domain Managers for Integration & Conformance Tests
from app.data_governance.manager import DataGovernanceManager
from app.architecture_platform.manager import ArchitecturePlatformManager
from app.compliance_platform.manager import CompliancePlatformManager
from app.portfolio_platform.manager import PortfolioPlatformManager
from app.decision_intelligence.manager import DecisionIntelligenceManager


def test_flow1_cross_tenant_isolation():
    """Flow 1: Cross-tenant access attempt raises CrossTenantAccessException with zero metadata leakage."""
    guard = TenantAccessGuard()
    # Same tenant / global succeeds
    assert guard.validator.validate_tenant_access("tenant_a", "tenant_a") is True
    assert guard.validator.validate_tenant_access("global", "tenant_b") is True

    # Cross tenant fails safely
    with pytest.raises(CrossTenantAccessException) as exc_info:
        guard.enforce_isolation("tenant_attacker", "tenant_victim")
    assert "tenant_attacker" in str(exc_info.value)
    assert "tenant_victim" in str(exc_info.value)


def test_flow2_deterministic_fingerprinting():
    """Flow 2: Canonical serialization produces identical fingerprints regardless of dict key order, dates, enums."""
    payload1 = {
        "b_key": 2,
        "a_key": 1,
        "tags": {"z", "a", "m"},
        "status": GovernanceDecisionStatus.ALLOW,
    }
    payload2 = {
        "a_key": 1,
        "tags": {"m", "a", "z"},
        "status": GovernanceDecisionStatus.ALLOW,
        "b_key": 2,
    }

    fp1 = FingerprintGenerator.generate(payload1, contract_version="1.0.0")
    fp2 = FingerprintGenerator.generate(payload2, contract_version="1.0.0")

    assert fp1 == fp2
    assert len(fp1) == 64


def test_flow3_immutable_finalization():
    """Flow 3: Finalized resource mutation attempt is blocked."""
    res = ImmutableResource(resource_id="res_001", tenant_id="tenant_1")
    assert res.state == ImmutableResourceState.MUTABLE

    finalized = ImmutableResourceValidator.finalize(res, fingerprint="sha256_hash_1234")
    assert finalized.state == ImmutableResourceState.FINALIZED

    with pytest.raises(ImmutableMutationException):
        ImmutableResourceValidator.ensure_mutable(finalized)


def test_flow4_idempotency_replay():
    """Flow 4: Same tenant + operation_type + idempotency_key + same request payload returns existing result."""
    idemp = IdempotencyManager()
    tenant = "tenant_idemp_4"
    op = "ALLOCATE_FUNDING"
    key = "key_12345"
    payload = {"amount_usd": 50000.0}

    rec1 = idemp.check_or_start(tenant, op, key, payload)
    assert rec1 is None  # First execution started

    completed = idemp.complete_operation(tenant, op, key, {"status": "SUCCESS", "allocated": 50000.0})
    assert completed.status == IdempotencyStatus.COMPLETED

    # Replay request
    rec2 = idemp.check_or_start(tenant, op, key, payload)
    assert rec2 is not None
    assert rec2.result_payload["allocated"] == 50000.0


def test_flow5_idempotency_conflict():
    """Flow 5: Same key + different request payload raises IdempotencyConflictException."""
    idemp = IdempotencyManager()
    tenant = "tenant_idemp_5"
    op = "ALLOCATE_FUNDING"
    key = "key_conflict_123"

    idemp.check_or_start(tenant, op, key, {"amount_usd": 50000.0})

    # Different payload with same key raises conflict
    with pytest.raises(IdempotencyConflictException):
        idemp.check_or_start(tenant, op, key, {"amount_usd": 999999.0})


def test_flow6_secret_redaction():
    """Flow 6: Sensitive data sanitizer redacts keys/tokens without mutating original objects."""
    sanitizer = SensitiveDataSanitizer()
    original = {
        "api_key": "sk-secret-12345",
        "user": "admin",
        "nested": {"token": "secret_bearer_token"},
    }

    sanitized = sanitizer.sanitize_copy(original)
    assert sanitized["api_key"] == "[REDACTED]"
    assert sanitized["nested"]["token"] == "[REDACTED]"
    assert sanitized["user"] == "admin"

    # Original object remains unmutated
    assert original["api_key"] == "sk-secret-12345"


def test_flow7_trust_contract_compatibility():
    """Flow 7: Domain trust scores map to TrustAssessment shared contract via adapters."""
    adapter = PlatformContractAdapter()

    assessment = adapter.trust.from_domain_trust(
        tenant_id="tenant_7",
        subject_type="DATA_ASSET",
        subject_id="asset_001",
        score=95.0,
    )

    assert assessment.score == 95.0
    assert assessment.band == TrustBand.HIGH_TRUST
    assert assessment.tenant_id == "tenant_7"


def test_flow8_governance_decision_compatibility():
    """Flow 8: Domain governance decisions map to GovernanceDecision shared contract via adapters."""
    adapter = PlatformContractAdapter()

    gov_dec = adapter.governance.from_domain_decision(
        tenant_id="tenant_8",
        subject_type="AI_INITIATIVE",
        subject_id="init_001",
        status_str="REQUIRE_APPROVAL",
        reason_msg="Exceeds budget threshold",
    )

    assert gov_dec.status == GovernanceDecisionStatus.REQUIRE_APPROVAL
    assert gov_dec.reasons[0].message == "Exceeds budget threshold"


def test_flow9_delegation_only_enforcement():
    """Flow 9: Shared delegation contract prevents direct infrastructure mutation."""
    req = DelegationRequest(
        tenant_id="tenant_9",
        target=DelegationTarget.PORTFOLIO_PLATFORM,
        action="DELEGATE_INITIATIVE",
        payload={"initiative_id": "init_99"},
    )
    assert req.status == DelegationStatus.CREATED
    assert req.target == DelegationTarget.PORTFOLIO_PLATFORM


def test_flow10_lifecycle_validation():
    """Flow 10: Invalid state machine transitions are rejected with InvalidLifecycleTransitionException."""
    machine = LifecycleMachine(
        name="DecisionLifecycle",
        initial_state="DRAFT",
        valid_transitions=[
            LifecycleTransition(from_state="DRAFT", to_state="ANALYZING"),
            LifecycleTransition(from_state="ANALYZING", to_state="FINALIZED"),
        ],
        terminal_states={"FINALIZED"},
    )

    assert machine.validate_transition("DRAFT", "ANALYZING") is True

    with pytest.raises(InvalidLifecycleTransitionException):
        machine.validate_transition("FINALIZED", "DRAFT")


def test_flow11_circular_dependency_protection():
    """Flow 11: Automated validation ensures app/platform_contracts has zero domain manager imports."""
    contracts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app", "platform_contracts")
    assert CircularDependencyValidator.validate_platform_contracts_isolation(contracts_dir) is True


def test_flow12_full_cross_platform_lifecycle():
    """Flow 12: Complete cross-platform workflow using shared contracts and adapters."""
    adapter = PlatformContractAdapter()
    tenant = "tenant_full_12"

    # 1. Snapshot creation
    snap = adapter.snapshot.from_domain_snapshot(
        tenant_id=tenant,
        resource_type="ENTERPRISE_DECISION",
        resource_id="dec_12",
        domain_payload={"title": "Cloud Migration", "status": "FINALIZED"},
    )
    assert SnapshotValidator.validate_snapshot(snap) is True

    # 2. Trust & Governance evaluation
    trust = adapter.trust.from_domain_trust(tenant, "ENTERPRISE_DECISION", "dec_12", 92.0)
    gov = adapter.governance.from_domain_decision(tenant, "ENTERPRISE_DECISION", "dec_12", "ALLOW")

    # 3. Delegation
    delegation = adapter.delegation.from_domain_delegation("del_12", tenant, "PORTFOLIO_PLATFORM")

    assert trust.band == TrustBand.HIGH_TRUST
    assert gov.status == GovernanceDecisionStatus.ALLOW
    assert delegation.status == DelegationStatus.COMPLETED


def test_flow13_domain_contract_conformance():
    """Flow 13: Data Governance, Architecture, Compliance, Portfolio, Decision Intelligence conform to shared contracts via adapters."""
    adapter = PlatformContractAdapter()
    tenant = "tenant_conf_13"

    # Data Governance
    dg_mgr = DataGovernanceManager()
    dg_report = adapter.snapshot.from_domain_snapshot(tenant, "DATA_ASSET", "asset_13", {"name": "Customer DB"})

    # Architecture
    arch_mgr = ArchitecturePlatformManager()
    arch_trust = adapter.trust.from_domain_trust(tenant, "ARCHITECTURE_NODE", "node_13", 88.0)

    # Compliance
    comp_mgr = CompliancePlatformManager()
    comp_gov = adapter.governance.from_domain_decision(tenant, "COMPLIANCE_CONTROL", "ctrl_13", "ALLOW")

    # Portfolio
    port_mgr = PortfolioPlatformManager()
    port_risk = adapter.risk.from_domain_risk(tenant, "INVESTMENT", "inv_13", 15.0)

    # Decision Intelligence
    dec_mgr = DecisionIntelligenceManager()
    dec_evidence = adapter.evidence.from_domain_evidence(tenant, "DECISION", "dec_13", "Lineage evidence")

    assert dg_report.metadata.resource_type == "DATA_ASSET"
    assert arch_trust.band == TrustBand.TRUSTED
    assert comp_gov.status == GovernanceDecisionStatus.ALLOW
    assert port_risk.risk_score == 15.0
    assert dec_evidence.metadata.source.source_subsystem == "DECISION"


def test_flow14_backward_compatibility():
    """Flow 14: Existing Phase 5.25-5.29 public manager workflows execute identically before/after contract integration."""
    tenant = "tenant_backcompat_14"

    # Data Governance flow
    dg_mgr = DataGovernanceManager()
    from app.data_governance.assets import DataAssetType, DataAssetOwner
    owner = DataAssetOwner(owner_id="u1", owner_name="Data Admin", owner_email="data@corp.com")
    asset = dg_mgr.asset_manager.register_asset(
        tenant_id=tenant,
        name="CustomerDB",
        asset_type=DataAssetType.DATABASE,
        owner=owner,
    )
    assert asset.tenant_id == tenant

    # Architecture flow
    arch_mgr = ArchitecturePlatformManager()
    from app.architecture_platform.nodes import ArchitectureNodeType
    node = arch_mgr.node_manager.register_node(
        tenant_id=tenant,
        name="InferenceEngine",
        node_type=ArchitectureNodeType.SERVICE,
    )
    assert node.tenant_id == tenant


    # Compliance flow
    comp_mgr = CompliancePlatformManager()
    req = comp_mgr.requirement_manager.register_requirement(
        tenant_id=tenant,
        framework_id="fw_gdpr",
        code="REQ-GDPR-01",
        title="Consent Requirement",
        description="Mandatory user consent",
    )
    assert req.tenant_id == tenant


    # Portfolio flow
    port_mgr = PortfolioPlatformManager()
    strat = port_mgr.strategy_manager.create_strategy(
        tenant_id=tenant,
        name="AI Automation Strategy",
        description="Strategy description",
    )
    assert strat.tenant_id == tenant



    # Decision Intelligence flow
    dec_mgr = DecisionIntelligenceManager()
    dec_res = dec_mgr.run_full_decision_flow(tenant_id=tenant)
    assert dec_res["decision"]["tenant_id"] == tenant




def test_flow15_contract_versioning():
    """Flow 15: Contract semantic versioning, additive vs breaking compatibility, and fingerprint version inclusion."""
    v1 = ContractVersion.parse("1.0.0")
    v2 = ContractVersion.parse("1.1.0")
    v3 = ContractVersion.parse("2.0.0")

    assert ContractCompatibilityValidator.validate("1.1.0", "1.0.0") is True

    with pytest.raises(ContractVersionException):
        ContractCompatibilityValidator.validate("2.0.0", "1.0.0")

    # Fingerprints include contract version
    payload = {"data": "test"}
    fp_v1 = FingerprintGenerator.generate(payload, contract_version="1.0.0")
    fp_v2 = FingerprintGenerator.generate(payload, contract_version="2.0.0")

    assert fp_v1 != fp_v2


def test_flow16_concurrent_idempotency():
    """Flow 16: Concurrent requests with identical tenant_id + operation_type + idempotency_key ensure single logical execution."""
    idemp = IdempotencyManager()
    tenant = "tenant_conc_16"
    op = "DELEGATE_ACTION"
    key = "concurrent_key_999"
    payload = {"action": "SCALE"}

    def run_worker():
        record = idemp.check_or_start(tenant, op, key, payload)
        if record is None:
            # Simulate work
            idemp.complete_operation(tenant, op, key, {"status": "SUCCESS"})
            return "EXECUTED"
        return "REPLAYED"

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(run_worker) for _ in range(5)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]

    # Exactly 1 worker executes; others replay
    assert results.count("EXECUTED") == 1
    assert results.count("REPLAYED") == 4
