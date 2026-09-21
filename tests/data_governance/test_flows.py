"""Mandatory End-to-End Tests for Enterprise AI Data Governance Platform (Phase 5.25)."""

import pytest

from app.data_governance.access import DataAccessDecisionType, DataAccessRequest, DataAction, PrincipalType
from app.data_governance.assets import DataAssetOwner, DataAssetType, DataDomain
from app.data_governance.consent import ConsentPurpose
from app.data_governance.exceptions import (
    CrossTenantDataAccessException,
    RetentionPolicyViolationException,
)
from app.data_governance.lineage import LineageNodeType
from app.data_governance.manager import DataGovernanceManager
from app.data_governance.retention import LifecycleState, RetentionAction
from app.data_governance.sharing import DataSharingScope
from app.data_governance.trust import TrustBand


@pytest.fixture
def gov_mgr():
    return DataGovernanceManager()


def test_flow_1_governed_ai_data_access(gov_mgr):
    """Flow 1: Governed AI Data Access chain from Identity -> Tenant -> Asset -> Consent -> Policy -> Trust -> Masking -> Audit."""
    tenant_id = "tenant_corp"
    owner = DataAssetOwner(owner_id="usr_alice", owner_name="Alice", owner_email="alice@corp.com")

    # 1. Register & Govern Asset with PII content sample
    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_id,
        name="Customer Profiling Dataset",
        asset_type=DataAssetType.DATASET,
        owner=owner,
        domain=DataDomain.CUSTOMER,
        content_sample="Contains customer email and ssn fields",
    )

    asset_id = reg["asset"]["asset_id"]

    # Classification should be RESTRICTED due to PII rule
    assert reg["asset"]["classification"] == "RESTRICTED"

    # 2. Grant Consent for AI_CONTEXT
    gov_mgr.consent_manager.grant_consent(
        tenant_id=tenant_id,
        subject_id="usr_bob",
        purposes=[ConsentPurpose.AI_CONTEXT],
        allowed_asset_ids=[asset_id],
    )

    # 3. Evaluate Pre-Retrieval Access
    req = DataAccessRequest(
        tenant_id=tenant_id,
        principal_id="usr_bob",
        principal_type=PrincipalType.AGENT,
        asset_id=asset_id,
        action=DataAction.RETRIEVE_CONTEXT,
        purpose=ConsentPurpose.AI_CONTEXT,
    )

    decision = gov_mgr.evaluate_access(req)

    assert decision.allowed is True
    assert decision.decision == DataAccessDecisionType.MASK
    assert decision.requires_masking is True
    assert decision.snapshot.trust_score >= 70.0

    # 4. Audit Event Recorded
    events = gov_mgr.usage_manager.list_usage_events(tenant_id=tenant_id, asset_id=asset_id)
    assert len(events) == 1
    assert events[0].authorization_decision == "MASK"


def test_flow_2_data_contract_violation(gov_mgr):
    """Flow 2: Data Contract Violation & Breaking Change Detection."""
    tenant_id = "tenant_producer"
    owner = DataAssetOwner(owner_id="dev_charlie", owner_name="Charlie", owner_email="charlie@prod.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_id,
        name="Orders Stream",
        asset_type=DataAssetType.EVENT_STREAM,
        owner=owner,
    )
    asset_id = reg["asset"]["asset_id"]

    # Define contract
    from app.data_governance.contracts import ContractRule, ContractSchema

    spec = ContractSchema(
        fields={
            "order_id": ContractRule(field_name="order_id", expected_type="string", required=True),
            "amount": ContractRule(field_name="amount", expected_type="float", required=True),
        }
    )
    gov_mgr.contract_manager.create_contract(
        tenant_id=tenant_id,
        asset_id=asset_id,
        schema_spec=spec,
        owner_id="dev_charlie",
    )

    # Producer attempts breaking schema change (missing required field 'amount' & type mismatch)
    incoming_schema = {"order_id": "string", "amount": "string"}
    val_res = gov_mgr.contract_manager.validate_producer_schema(
        tenant_id=tenant_id,
        asset_id=asset_id,
        incoming_schema=incoming_schema,
    )

    assert val_res.is_valid is False
    assert val_res.is_breaking_change is True
    assert val_res.requires_approval is True
    assert val_res.approval_request_id is not None


def test_flow_3_low_quality_data(gov_mgr):
    """Flow 3: Low Quality Data triggers incident and drops trust score."""
    tenant_id = "tenant_analytics"
    owner = DataAssetOwner(owner_id="steward_dave", owner_name="Dave", owner_email="dave@analytics.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_id,
        name="Raw Clickstream Data",
        asset_type=DataAssetType.ANALYTICS_DATASET,
        owner=owner,
    )
    asset_id = reg["asset"]["asset_id"]

    # Evaluate quality with corrupt/empty records
    sample_records = [{"field1": None}, {"field1": None}]  # Extremely low completeness
    qual_res = gov_mgr.quality_manager.evaluate_quality(
        tenant_id=tenant_id,
        asset_id=asset_id,
        sample_records=sample_records,
        freshness_seconds=36000,
    )

    assert qual_res.has_critical_violation is True
    assert qual_res.overall_score < 70.0

    # Trust score drops
    trust = gov_mgr.trust_engine.calculate_trust_score(
        tenant_id=tenant_id,
        asset_id=asset_id,
        quality_score=qual_res.overall_score,
        freshness_score=30.0,
        lineage_score=20.0,
        source_reliability=30.0,
        contract_compliance=30.0,
        security_compliance=30.0,
        privacy_compliance=30.0,
        usage_history=30.0,
    )
    assert trust.overall_score < 50.0

    assert trust.trust_band == TrustBand.UNTRUSTED


def test_flow_4_privacy_consent_withdrawal(gov_mgr):
    """Flow 4: Privacy & Consent Withdrawal revokes access and blocks future attempts."""
    tenant_id = "tenant_health"
    subject_id = "patient_123"
    owner = DataAssetOwner(owner_id="dr_smith", owner_name="Dr Smith", owner_email="smith@health.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_id,
        name="Patient Health Record",
        asset_type=DataAssetType.DOCUMENT,
        owner=owner,
        content_sample="medical_record prescription diagnosis",
    )
    asset_id = reg["asset"]["asset_id"]

    # Grant consent
    gov_mgr.consent_manager.grant_consent(
        tenant_id=tenant_id,
        subject_id=subject_id,
        purposes=[ConsentPurpose.PERSONALIZATION],
        allowed_asset_ids=[asset_id],
    )

    # Initial access allowed
    req1 = DataAccessRequest(
        tenant_id=tenant_id,
        principal_id=subject_id,
        asset_id=asset_id,
        purpose=ConsentPurpose.PERSONALIZATION,
    )
    dec1 = gov_mgr.evaluate_access(req1)
    assert dec1.allowed is True

    # Withdraw consent with idempotency_key
    gov_mgr.consent_manager.withdraw_consent(
        tenant_id=tenant_id,
        subject_id=subject_id,
        idempotency_key="withdraw_123",
    )

    # Future access attempt blocked
    dec2 = gov_mgr.evaluate_access(req1)
    assert dec2.allowed is False
    assert dec2.decision == DataAccessDecisionType.BLOCK
    assert "Consent missing or withdrawn" in dec2.reason


def test_flow_5_data_lineage(gov_mgr):
    """Flow 5: Complete tenant-isolated lineage tracking."""
    tenant_id = "tenant_fin"

    # Record pipeline lineage: SOURCE -> INGESTION -> TRANSFORMATION -> KNOWLEDGE -> AGENT
    gov_mgr.lineage_manager.record_lineage_event(
        tenant_id=tenant_id,
        actor_identity="pipeline_ingest",
        source_id="src_db",
        source_name="Postgres DB",
        source_type=LineageNodeType.SOURCE,
        target_id="ds_raw",
        target_name="Raw Data Table",
        target_type=LineageNodeType.INGESTION,
        operation="EXTRACT",
    )

    gov_mgr.lineage_manager.record_lineage_event(
        tenant_id=tenant_id,
        actor_identity="spark_job",
        source_id="ds_raw",
        source_name="Raw Data Table",
        source_type=LineageNodeType.INGESTION,
        target_id="ds_clean",
        target_name="Cleaned Dataset",
        target_type=LineageNodeType.TRANSFORMATION,
        operation="TRANSFORM",
    )

    lineage = gov_mgr.lineage_manager.get_asset_lineage("ds_clean", tenant_id=tenant_id)
    assert len(lineage.nodes) == 3
    assert len(lineage.edges) == 2

    # Verify tenant isolation: tenant_other sees empty lineage
    other_lineage = gov_mgr.lineage_manager.get_asset_lineage("ds_clean", tenant_id="tenant_other")
    assert len(other_lineage.nodes) == 0


def test_flow_6_high_risk_data_sharing(gov_mgr):
    """Flow 6: High-Risk Cross-Tenant Data Sharing require approval and audit."""
    source_tenant = "tenant_bank_a"
    target_tenant = "tenant_bank_b"
    owner = DataAssetOwner(owner_id="bank_admin", owner_name="Admin", owner_email="admin@banka.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=source_tenant,
        name="Shared Risk Profile",
        asset_type=DataAssetType.ANALYTICS_DATASET,
        owner=owner,
    )
    asset_id = reg["asset"]["asset_id"]

    # Request cross-tenant share
    agreement = gov_mgr.sharing_manager.request_cross_tenant_share(
        source_tenant_id=source_tenant,
        target_tenant_id=target_tenant,
        asset_id=asset_id,
        scope=DataSharingScope.CROSS_ORGANIZATION,
    )

    # Default is unapproved
    assert agreement.approved is False
    assert agreement.approval_request_id is not None
    assert gov_mgr.sharing_manager.validate_sharing_authorization(source_tenant, target_tenant, asset_id) is False

    # Approve agreement
    gov_mgr.sharing_manager.approve_share_agreement(agreement.agreement_id, approver_id="compliance_officer")
    assert gov_mgr.sharing_manager.validate_sharing_authorization(source_tenant, target_tenant, asset_id) is True


def test_flow_7_retention_lifecycle(gov_mgr):
    """Flow 7: Retention evaluation, Legal Hold protection, delegation-only execution with idempotency."""
    tenant_id = "tenant_legal"
    owner = DataAssetOwner(owner_id="legal_user", owner_name="Legal", owner_email="legal@corp.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_id,
        name="Contract Document",
        asset_type=DataAssetType.DOCUMENT,
        owner=owner,
    )
    asset_id = reg["asset"]["asset_id"]

    # Place legal hold
    hold = gov_mgr.retention_manager.place_legal_hold(
        tenant_id=tenant_id,
        asset_id=asset_id,
        reason="Pending Litigation",
        case_reference="CASE-2026-99",
        placed_by="legal_counsel",
    )

    # Retention evaluation recognizes legal hold
    eval_res = gov_mgr.retention_manager.evaluate_retention(tenant_id=tenant_id, asset_id=asset_id, asset_age_days=1000)
    assert eval_res.recommended_action == RetentionAction.LEGAL_HOLD
    assert eval_res.is_legal_hold_active is True

    # Attempting execution while under hold raises exception
    with pytest.raises(RetentionPolicyViolationException):
        gov_mgr.retention_manager.prepare_delegated_execution(
            tenant_id=tenant_id,
            asset_id=asset_id,
            action=RetentionAction.DELETE,
            idempotency_key="del_key_1",
        )

    # Release legal hold
    gov_mgr.retention_manager.release_legal_hold(hold.hold_id, asset_id)

    # Prepare execution successfully now
    exec_rec = gov_mgr.retention_manager.prepare_delegated_execution(
        tenant_id=tenant_id,
        asset_id=asset_id,
        action=RetentionAction.DELETE,
        idempotency_key="del_key_1",
    )
    assert exec_rec.state == LifecycleState.PENDING

    # Duplicate call returns same execution record (idempotency)
    exec_rec_dup = gov_mgr.retention_manager.prepare_delegated_execution(
        tenant_id=tenant_id,
        asset_id=asset_id,
        action=RetentionAction.DELETE,
        idempotency_key="del_key_1",
    )
    assert exec_rec_dup.execution_id == exec_rec.execution_id


def test_flow_8_low_trust_data(gov_mgr):
    """Flow 8: Low Trust Data blocks high-risk AI decisions or requires human approval."""
    tenant_id = "tenant_ai"
    owner = DataAssetOwner(owner_id="data_sci", owner_name="DataSci", owner_email="sci@ai.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_id,
        name="Unverified Web Scraping",
        asset_type=DataAssetType.MODEL_DATASET,
        owner=owner,
    )
    asset_id = reg["asset"]["asset_id"]

    # Calculate low trust score
    trust = gov_mgr.trust_engine.calculate_trust_score(
        tenant_id=tenant_id,
        asset_id=asset_id,
        quality_score=30.0,
        freshness_score=20.0,
        lineage_score=20.0,
        source_reliability=30.0,
        contract_compliance=40.0,
        security_compliance=40.0,
        privacy_compliance=40.0,
        usage_history=30.0,
    )
    assert trust.overall_score < 50.0

    # Decision intelligence composite check
    ai_eval = gov_mgr.trust_engine.evaluate_ai_decision_trust(
        data_trust_score=trust.overall_score,
        decision_trust_score=50.0,
        risk_level="HIGH",
    )
    assert ai_eval["recommended_action"] == "BLOCK"


def test_flow_9_cross_tenant_isolation(gov_mgr):
    """Flow 9: Cross-tenant isolation prevents metadata, raw data, lineage, or analytics leakage."""
    tenant_a = "tenant_alpha"
    tenant_b = "tenant_beta"
    owner_a = DataAssetOwner(owner_id="alice", owner_name="Alice", owner_email="a@alpha.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_a,
        name="Alpha Secret Vault",
        asset_type=DataAssetType.DATABASE,
        owner=owner_a,
    )
    asset_id = reg["asset"]["asset_id"]

    # Tenant B attempts to get Tenant A's asset directly
    with pytest.raises(CrossTenantDataAccessException):
        gov_mgr.asset_manager.get_asset(asset_id, tenant_id=tenant_b)

    # Tenant B lists assets -> Sees 0 assets
    b_assets = gov_mgr.asset_manager.list_assets(tenant_id=tenant_b)
    assert len(b_assets) == 0

    # Analytics for Tenant B shows zero assets
    b_report = gov_mgr.analytics_engine.generate_report(tenant_id=tenant_b)
    assert b_report.governed_assets_count == 0


def test_flow_10_sensitive_data_redaction(gov_mgr):
    """Flow 10: Secret and Sensitive Data Redaction in usage events & telemetry."""
    tenant_id = "tenant_sec"
    owner = DataAssetOwner(owner_id="sec_admin", owner_name="SecAdmin", owner_email="sec@corp.com")

    reg = gov_mgr.register_and_govern_asset(
        tenant_id=tenant_id,
        name="Auth Credentials Table",
        asset_type=DataAssetType.TABLE,
        owner=owner,
        content_sample="password api_key secret_token",
    )
    asset_id = reg["asset"]["asset_id"]

    # Evaluate access with context containing metadata
    req = DataAccessRequest(
        tenant_id=tenant_id,
        principal_id="sec_auditor",
        asset_id=asset_id,
        context={"request_ip": "10.0.0.1"},
    )
    gov_mgr.evaluate_access(req)

    # Check logged usage event metadata does NOT contain passwords or raw secret tokens
    events = gov_mgr.usage_manager.list_usage_events(tenant_id=tenant_id, asset_id=asset_id)
    assert len(events) == 1
    event_dict = events[0].model_dump()
    event_str = str(event_dict)

    assert "password" not in event_str
    assert "api_key" not in event_str
    assert "secret_token" not in event_str
