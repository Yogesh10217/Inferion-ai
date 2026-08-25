"""Domain Compatibility Adapters Subsystem (Phase 5.30)."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence
from app.platform_contracts.snapshots import PlatformSnapshot, SnapshotMetadata, SnapshotFactory
from app.platform_contracts.governance import GovernanceDecision, GovernanceDecisionStatus, GovernanceDecisionReason
from app.platform_contracts.risk import RiskAssessmentReference, RiskReference, RiskLevel

from app.platform_contracts.approvals import ApprovalReference, ApprovalStatusReference
from app.platform_contracts.evidence import EvidenceReference, EvidenceMetadata, EvidenceSourceReference, EvidenceStrength, EvidenceIntegrity
from app.platform_contracts.delegation import DelegationReference, DelegationTarget, DelegationStatus


class TrustAssessmentAdapter:
    """Adapts domain-specific trust scores to shared TrustAssessment."""

    @staticmethod
    def from_domain_trust(
        tenant_id: str,
        subject_type: str,
        subject_id: str,
        score: float,
        band_str: Optional[str] = None,
        version: str = "1.0.0",
    ) -> TrustAssessment:
        band = None
        if band_str:
            try:
                band = TrustBand(band_str)
            except Exception:
                pass
        if not band:
            if score >= 90.0:
                band = TrustBand.HIGH_TRUST
            elif score >= 70.0:
                band = TrustBand.TRUSTED
            elif score >= 50.0:
                band = TrustBand.RESTRICTED
            else:
                band = TrustBand.UNTRUSTED

        return TrustAssessment(
            tenant_id=tenant_id,
            subject_type=subject_type,
            subject_id=subject_id,
            score=score,
            band=band,
            confidence=TrustConfidence.HIGH,
            version=version,
        )



class SnapshotAdapter:
    """Adapts domain snapshot objects to shared PlatformSnapshot."""

    @staticmethod
    def from_domain_snapshot(
        tenant_id: str,
        resource_type: str,
        resource_id: str,
        domain_payload: Dict[str, Any],
        version: str = "1.0.0",
        policy_version: str = "1.0.0",
        contract_version: str = "1.0.0",
    ) -> PlatformSnapshot:
        return SnapshotFactory.create_snapshot(
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            domain_payload=domain_payload,
            version=version,
            policy_version=policy_version,
            contract_version=contract_version,
        )


class GovernanceDecisionAdapter:
    """Adapts domain governance decisions to shared GovernanceDecision."""

    @staticmethod
    def from_domain_decision(
        tenant_id: str,
        subject_type: str,
        subject_id: str,
        status_str: str = "ALLOW",
        reason_msg: str = "Decision evaluated",
    ) -> GovernanceDecision:
        try:
            status = GovernanceDecisionStatus(status_str)
        except Exception:
            status = GovernanceDecisionStatus.ALLOW

        return GovernanceDecision(
            tenant_id=tenant_id,
            subject_type=subject_type,
            subject_id=subject_id,
            status=status,
            reasons=[GovernanceDecisionReason(code="GOV_DECISION", message=reason_msg)],
        )


class RiskReferenceAdapter:
    """Adapts domain risk profiles to shared RiskAssessmentReference."""

    @staticmethod
    def from_domain_risk(
        tenant_id: str,
        subject_type: str,
        subject_id: str,
        risk_score: float,
        risk_level_str: str = "LOW",
    ) -> RiskAssessmentReference:
        try:
            r_level = RiskLevel(risk_level_str)
        except Exception:
            r_level = RiskLevel.LOW

        return RiskAssessmentReference(
            tenant_id=tenant_id,
            subject_type=subject_type,
            subject_id=subject_id,
            risk_score=risk_score,
            risk_level=r_level,
        )


class ApprovalReferenceAdapter:
    """Adapts domain approval objects to shared ApprovalReference."""

    @staticmethod
    def from_domain_approval(
        approval_id: str,
        tenant_id: str,
        action_type: str,
        status_str: str = "PENDING",
    ) -> ApprovalReference:
        try:
            status = ApprovalStatusReference(status_str)
        except Exception:
            status = ApprovalStatusReference.PENDING

        return ApprovalReference(
            approval_id=approval_id,
            tenant_id=tenant_id,
            action_type=action_type,
            approval_status=status,
        )


class EvidenceReferenceAdapter:
    """Adapts domain evidence objects to shared EvidenceReference."""

    @staticmethod
    def from_domain_evidence(
        tenant_id: str,
        source_subsystem: str,
        source_entity_id: str,
        description: str,
        strength_str: str = "STRONG",
    ) -> EvidenceReference:
        try:
            strength = EvidenceStrength(strength_str)
        except Exception:
            strength = EvidenceStrength.STRONG

        meta = EvidenceMetadata(
            tenant_id=tenant_id,
            source=EvidenceSourceReference(source_subsystem=source_subsystem, source_entity_id=source_entity_id),
            strength=strength,
            integrity=EvidenceIntegrity.VERIFIED,
        )
        return EvidenceReference(metadata=meta, description=description)


class DelegationAdapter:
    """Adapts domain delegation objects to shared DelegationReference."""

    @staticmethod
    def from_domain_delegation(
        delegation_id: str,
        tenant_id: str,
        target_str: str = "PORTFOLIO_PLATFORM",
        status_str: str = "COMPLETED",
    ) -> DelegationReference:
        try:
            target = DelegationTarget(target_str)
        except Exception:
            target = DelegationTarget.PORTFOLIO_PLATFORM

        try:
            status = DelegationStatus(status_str)
        except Exception:
            status = DelegationStatus.COMPLETED

        return DelegationReference(
            delegation_id=delegation_id,
            tenant_id=tenant_id,
            target=target,
            status=status,
        )


class PlatformContractAdapter:
    """Coordinator adapter for all domain-to-shared contract translations."""

    trust = TrustAssessmentAdapter()
    snapshot = SnapshotAdapter()
    governance = GovernanceDecisionAdapter()
    risk = RiskReferenceAdapter()
    approval = ApprovalReferenceAdapter()
    evidence = EvidenceReferenceAdapter()
    delegation = DelegationAdapter()
