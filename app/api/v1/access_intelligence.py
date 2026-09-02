"""REST API Router for Enterprise AI Access Intelligence Platform (Phase 5.39)."""

from fastapi import APIRouter, HTTPException, Depends, Header, Query
from typing import Dict, Any, Optional, List

from app.access_intelligence.manager import AccessIntelligenceManager
from app.access_intelligence.exceptions import AccessIntelligenceException
from app.access_intelligence.identities import IdentityType, IdentityRiskLevel
from app.access_intelligence.entitlements import EntitlementType
from app.access_intelligence.privileged_access import PrivilegedAccessScope
from app.access_intelligence.emergency_access import EmergencyAccessReason
from app.access_intelligence.access_reviews import AccessReviewScope, AccessReviewDecision
from app.access_intelligence.certifications import CertificationScope, CertificationDecision
from app.access_intelligence.remediation import AccessRemediationAction

router = APIRouter(prefix="/v1/access", tags=["Access Intelligence"])

_global_access_manager = AccessIntelligenceManager()


def get_access_manager() -> AccessIntelligenceManager:
    return _global_access_manager


@router.get("/identities")
def list_identities(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    identity_type: Optional[str] = Query(None),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        type_enum = IdentityType(identity_type) if identity_type else None
        identities = mgr.identity_manager.list_identities(tenant_id, identity_type=type_enum)
        return [i.model_dump(mode="json") for i in identities]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/identities")
def register_identity(
    name: str,
    external_id: str,
    identity_type: str = Query("HUMAN_USER"),
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        ident = mgr.identity_manager.register_identity(
            tenant_id=tenant_id,
            name=name,
            identity_type=IdentityType(identity_type),
            external_id=external_id,
        )
        return ident.model_dump(mode="json")
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/entitlements")
def list_entitlements(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    entitlement_type: Optional[str] = Query(None),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        type_enum = EntitlementType(entitlement_type) if entitlement_type else None
        entitlements = mgr.entitlement_manager.list_entitlements(tenant_id, entitlement_type=type_enum)
        return [e.model_dump(mode="json") for e in entitlements]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/relationships")
def list_relationships(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        rels = mgr.relationship_manager.list_relationships(tenant_id)
        return [r.model_dump(mode="json") for r in rels]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/authorization/evaluate")
def evaluate_authorization(
    subject_identity_id: str,
    action: str,
    resource_id: str,
    resource_type: str,
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        dec = mgr.authorization_manager.evaluate_authorization(
            tenant_id=tenant_id,
            subject_identity_id=subject_identity_id,
            action=action,
            resource_id=resource_id,
            resource_type=resource_type,
        )
        return dec.model_dump(mode="json")
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/least-privilege/{identity_id}")
def get_least_privilege_assessment(
    identity_id: str,
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        asm = mgr.least_privilege_manager.assess_identity(
            tenant_id=tenant_id,
            identity_id=identity_id,
            assigned_entitlement_ids=[],
            used_entitlement_ids=[],
        )
        return asm.model_dump(mode="json")
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/privileged-access")
def list_privileged_access(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        reqs = mgr.privileged_access_manager.list_requests(tenant_id)
        return [r.model_dump(mode="json") for r in reqs]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/privileged-access")
def request_privileged_access(
    requester_identity_id: str,
    target_role_or_entitlement: str,
    scope: str = Query("PRODUCTION"),
    justification: str = Query("Admin task"),
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        req = mgr.privileged_access_manager.request_privileged_access(
            tenant_id=tenant_id,
            requester_identity_id=requester_identity_id,
            target_role_or_entitlement=target_role_or_entitlement,
            scope=PrivilegedAccessScope(scope),
            justification=justification,
        )
        return req.model_dump(mode="json")
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/emergency-access")
def request_emergency_access(
    requester_identity_id: str,
    justification: str,
    reason: str = Query("SYSTEM_OUTAGE"),
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        req = mgr.emergency_access_manager.request_emergency_access(
            tenant_id=tenant_id,
            requester_identity_id=requester_identity_id,
            reason=EmergencyAccessReason(reason),
            justification=justification,
        )
        return req.model_dump(mode="json")
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/reviews")
def list_access_reviews(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        reviews = mgr.review_manager.list_reviews(tenant_id)
        return [r.model_dump(mode="json") for r in reviews]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/certifications")
def list_certifications(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        certs = mgr.certification_manager.list_certifications(tenant_id)
        return [c.model_dump(mode="json") for c in certs]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/anomalies")
def list_anomalies(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        anoms = mgr.anomaly_manager.list_anomalies(tenant_id)
        return [a.model_dump(mode="json") for a in anoms]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/investigations")
def list_investigations(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        invs = mgr.investigation_manager.list_investigations(tenant_id)
        return [i.model_dump(mode="json") for i in invs]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/remediation")
def list_remediation_plans(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        plans = mgr.remediation_manager.list_plans(tenant_id)
        return [p.model_dump(mode="json") for p in plans]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/verification")
def list_verifications(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        verifs = mgr.verification_manager.list_verifications(tenant_id)
        return [v.model_dump(mode="json") for v in verifs]
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.get("/analytics")
def get_analytics(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        report = mgr.analytics_engine.generate_report(tenant_id)
        return report.model_dump(mode="json")
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)


@router.post("/lifecycle/run")
def run_full_lifecycle(
    tenant_id: str = Header("default", alias="X-Tenant-ID"),
    mgr: AccessIntelligenceManager = Depends(get_access_manager),
):
    try:
        result = mgr.run_full_lifecycle(tenant_id)
        return result
    except AccessIntelligenceException as exc:
        raise HTTPException(status_code=400, detail=exc.message)
