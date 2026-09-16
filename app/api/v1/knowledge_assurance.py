"""FastAPI REST API endpoints for Phase 5.46 Knowledge Assurance platform."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeReferenceNotFoundException,
)
from app.knowledge_assurance.manager import KnowledgeAssuranceManager

router = APIRouter(prefix="/v1/knowledge", tags=["Knowledge Assurance"])

# Singleton manager instance
_manager = KnowledgeAssuranceManager()


def get_manager() -> KnowledgeAssuranceManager:
    return _manager


class CreateReferenceRequest(BaseModel):
    external_key: str
    resource_type: str = "DOCUMENT"
    classification: str = "INTERNAL"
    metadata: Dict[str, Any] = {}


class CreateSourceRequest(BaseModel):
    name: str
    source_type: str = "DOCUMENT_REPOSITORY"
    authority: str = "AUTHORITATIVE"
    reliability_score: float = 0.95


class CreateContextRequest(BaseModel):
    title: str
    context_type: str = "DECISION_CONTEXT"
    scope: str = "ORGANIZATION"
    priority: str = "HIGH"
    payload: Dict[str, Any] = {}


class AssembleContextRequest(BaseModel):
    target_resource_id: str
    required_concepts: List[str] = []
    min_trust_score: float = 0.8


@router.get("/status", response_model=Dict[str, Any])
def get_status(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    return mgr.get_status(tenant_id=x_tenant_id)


# References
@router.post("/references", response_model=Dict[str, Any])
def create_reference(
    req: CreateReferenceRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    try:
        ref = mgr.references_manager.register_reference(
            tenant_id=x_tenant_id,
            external_key=req.external_key,
            resource_type=req.resource_type,
            classification=req.classification,
            metadata=req.metadata,
        )
        return ref.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/references", response_model=List[Dict[str, Any]])
def list_references(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    refs = mgr.references_manager.list_references(tenant_id=x_tenant_id)
    return [r.model_dump() for r in refs]


@router.get("/references/{reference_id}", response_model=Dict[str, Any])
def get_reference(
    reference_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    try:
        ref = mgr.references_manager.get_reference(
            tenant_id=x_tenant_id, reference_id=reference_id
        )
        return ref.model_dump()
    except CrossTenantKnowledgeAssuranceException:
        raise HTTPException(status_code=403, detail="Access denied")
    except KnowledgeReferenceNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


# Sources
@router.post("/sources", response_model=Dict[str, Any])
def register_source(
    req: CreateSourceRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    try:
        source = mgr.sources_manager.register_source(
            tenant_id=x_tenant_id,
            name=req.name,
            source_type=req.source_type,
            authority=req.authority,
            reliability_score=req.reliability_score,
        )
        return source.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/sources", response_model=List[Dict[str, Any]])
def list_sources(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    sources = mgr.sources_manager.list_sources(tenant_id=x_tenant_id)
    return [s.model_dump() for s in sources]


# Context
@router.post("/context", response_model=Dict[str, Any])
def create_context(
    req: CreateContextRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    try:
        ctx = mgr.context_manager.create_context(
            tenant_id=x_tenant_id,
            title=req.title,
            context_type=req.context_type,
            scope=req.scope,
            priority=req.priority,
            payload=req.payload,
        )
        return ctx.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/context", response_model=List[Dict[str, Any]])
def list_contexts(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    ctxs = mgr.context_manager.list_contexts(tenant_id=x_tenant_id)
    return [c.model_dump() for c in ctxs]


# Context Assembly
@router.post("/context-assembly", response_model=Dict[str, Any])
def assemble_context(
    req: AssembleContextRequest,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    try:
        from app.knowledge_assurance.context_assembly import ContextAssemblyRequest

        assembly_req = ContextAssemblyRequest(
            tenant_id=x_tenant_id,
            target_resource_id=req.target_resource_id,
            required_concepts=req.required_concepts,
            min_trust_score=req.min_trust_score,
        )
        result = mgr.context_assembly_manager.assemble_context(
            tenant_id=x_tenant_id, request=assembly_req
        )
        return result.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Provenance
@router.get("/provenance/{target_resource_id}", response_model=Dict[str, Any])
def get_provenance(
    target_resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    prov = mgr.provenance_manager.record_provenance(
        tenant_id=x_tenant_id,
        target_resource_id=target_resource_id,
        sources=[{"source_id": "src-1", "origin_type": "USER_INPUT"}],
    )
    return prov.model_dump()


# Freshness
@router.get("/freshness/{target_resource_id}", response_model=Dict[str, Any])
def evaluate_freshness(
    target_resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    freshness = mgr.freshness_manager.evaluate_freshness(
        tenant_id=x_tenant_id, target_resource_id=target_resource_id
    )
    return freshness.model_dump()


# Trust
@router.get("/trust/{target_resource_id}", response_model=Dict[str, Any])
def evaluate_trust(
    target_resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    trust = mgr.trust_engine.evaluate_trust(
        tenant_id=x_tenant_id, target_resource_id=target_resource_id
    )
    return trust.model_dump()


# Confidence
@router.get("/confidence/{target_resource_id}", response_model=Dict[str, Any])
def evaluate_confidence(
    target_resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    conf = mgr.confidence_manager.evaluate_confidence(
        tenant_id=x_tenant_id, target_resource_id=target_resource_id
    )
    return conf.model_dump()


# Relevance
@router.get("/relevance/{target_resource_id}", response_model=Dict[str, Any])
def evaluate_relevance(
    target_resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    rel = mgr.relevance_manager.evaluate_relevance(
        tenant_id=x_tenant_id, target_resource_id=target_resource_id
    )
    return rel.model_dump()


# Conflicts
@router.get("/conflicts", response_model=List[Dict[str, Any]])
def list_conflicts(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    conflicts = mgr.conflict_manager.list_conflicts(tenant_id=x_tenant_id)
    return [c.model_dump() for c in conflicts]


# Consistency
@router.get("/consistency/{target_resource_id}", response_model=Dict[str, Any])
def assess_consistency(
    target_resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    cons = mgr.consistency_manager.assess_consistency(
        tenant_id=x_tenant_id, target_resource_id=target_resource_id
    )
    return cons.model_dump()


# Duplicates
@router.get("/duplicates", response_model=List[Dict[str, Any]])
def detect_duplicates(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    dups = mgr.duplication_manager.detect_duplicates(
        tenant_id=x_tenant_id, items=[{"id": "k1", "content": "Knowledge item"}]
    )
    return [d.model_dump() for d in dups]


# Gaps
@router.get("/gaps", response_model=List[Dict[str, Any]])
def analyze_gaps(
    domain: str = "GLOBAL",
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    gaps = mgr.gap_manager.analyze_domain_gaps(tenant_id=x_tenant_id, domain=domain)
    return [g.model_dump() for g in gaps]


# Coverage
@router.get("/coverage/{domain}", response_model=Dict[str, Any])
def evaluate_coverage(
    domain: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    cov = mgr.coverage_manager.evaluate_coverage(tenant_id=x_tenant_id, domain=domain)
    return cov.model_dump()


# Correlation
@router.get("/correlation/{resource_id}", response_model=List[Dict[str, Any]])
def correlate_knowledge(
    resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    corrs = mgr.correlation_manager.correlate_resource(
        tenant_id=x_tenant_id, target_resource_id=resource_id
    )
    return [c.model_dump() for c in corrs]


# Decision Context
@router.get("/decision-context/{decision_id}", response_model=Dict[str, Any])
def get_decision_context(
    decision_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    dctx = mgr.decision_context_manager.enrich_decision_context(
        tenant_id=x_tenant_id, decision_id=decision_id
    )
    return dctx.model_dump()


# Investigations
@router.get("/investigations", response_model=List[Dict[str, Any]])
def list_investigations(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    invs = mgr.investigation_manager.list_investigations(tenant_id=x_tenant_id)
    return [i.model_dump() for i in invs]


# Remediation
@router.get("/remediation", response_model=List[Dict[str, Any]])
def list_remediation_plans(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    plans = mgr.remediation_manager.list_plans(tenant_id=x_tenant_id)
    return [p.model_dump() for p in plans]


# Verification
@router.get("/verification", response_model=List[Dict[str, Any]])
def list_verifications(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    vers = mgr.verification_manager.list_verifications(tenant_id=x_tenant_id)
    return [v.model_dump() for v in vers]


# Evidence
@router.get("/evidence", response_model=List[Dict[str, Any]])
def list_evidence_bundles(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    bundles = mgr.evidence_manager.list_bundles(tenant_id=x_tenant_id)
    return [b.model_dump() for b in bundles]


# Assurance
@router.get("/assurance/{target_resource_id}", response_model=Dict[str, Any])
def assess_assurance(
    target_resource_id: str,
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    ass = mgr.assurance_manager.assess_knowledge_assurance(
        tenant_id=x_tenant_id, target_resource_id=target_resource_id
    )
    return ass.model_dump()


# Analytics
@router.get("/analytics/report", response_model=Dict[str, Any])
def get_analytics_report(
    x_tenant_id: str = Header(default="default_tenant"),
    mgr: KnowledgeAssuranceManager = Depends(get_manager),
):
    report = mgr.analytics_manager.build_report(tenant_id=x_tenant_id)
    return report.model_dump()
