"""REST API Router for Enterprise AI Knowledge Intelligence Platform (Phase 5.35)."""

from fastapi import APIRouter, HTTPException, Query, status
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.knowledge_intelligence.manager import KnowledgeIntelligenceManager
from app.knowledge_intelligence.knowledge import KnowledgeType, KnowledgeClassification
from app.knowledge_intelligence.sources import KnowledgeSourceType
from app.knowledge_intelligence.relationships import RelationshipType, RelationshipStrength
from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeNotFoundException,
    KnowledgeSourceNotFoundException,
    KnowledgeAccessDeniedException,
)

router = APIRouter(prefix="/v1/knowledge", tags=["Knowledge Intelligence"])
manager = KnowledgeIntelligenceManager()



class CreateKnowledgeItemRequest(BaseModel):
    title: str
    knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT
    classification: KnowledgeClassification = KnowledgeClassification.INTERNAL
    source_system: str = "INTERNAL"
    external_id: str = ""
    tags: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)


class CreateKnowledgeSourceRequest(BaseModel):
    name: str
    source_type: KnowledgeSourceType = KnowledgeSourceType.KNOWLEDGE_PLATFORM
    system_name: str = "KnowledgePlatform"
    endpoint_or_ref: str = "app.knowledge_platform"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CreateRelationshipRequest(BaseModel):
    source_id: str
    target_id: str
    relationship_type: RelationshipType = RelationshipType.RELATED_TO
    strength: RelationshipStrength = RelationshipStrength.STRONG
    evidence_description: str = "REST API Relationship Creation"


class RetrievalApiRequest(BaseModel):
    query: str
    max_classification: KnowledgeClassification = KnowledgeClassification.CRITICAL


class ContextApiRequest(BaseModel):
    item_ids: List[str]
    max_items: int = 10


class CreateRecommendationApiRequest(BaseModel):
    target_id: str
    title: str
    rationale: str
    is_high_risk: bool = False


class RecordMemoryApiRequest(BaseModel):
    key: str
    value_summary: str
    reference_id: str = ""


@router.post("/items")
def create_knowledge_item(req: CreateKnowledgeItemRequest, tenant_id: str = Query(...)):
    item = manager.knowledge_manager.register_knowledge(
        tenant_id=tenant_id,
        title=req.title,
        knowledge_type=req.knowledge_type,
        classification=req.classification,
        source_system=req.source_system,
        external_id=req.external_id,
        tags=req.tags,
        attributes=req.attributes,
    )
    return item.model_dump()


@router.get("/items")
def list_knowledge_items(tenant_id: str = Query(...), knowledge_type: Optional[KnowledgeType] = None):
    items = manager.knowledge_manager.list_knowledge(tenant_id, knowledge_type)
    return {"items": [i.model_dump() for i in items]}


@router.get("/items/{item_id}")
def get_knowledge_item(item_id: str, tenant_id: str = Query(...)):
    try:
        item = manager.knowledge_manager.get_knowledge(item_id, tenant_id)
        return item.model_dump()
    except CrossTenantKnowledgeAccessException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge item not found.")
    except KnowledgeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))



@router.post("/sources")
def create_knowledge_source(req: CreateKnowledgeSourceRequest, tenant_id: str = Query(...)):
    src = manager.source_manager.register_source(
        tenant_id=tenant_id,
        name=req.name,
        source_type=req.source_type,
        system_name=req.system_name,
        endpoint_or_ref=req.endpoint_or_ref,
        metadata=req.metadata,
    )
    return src.model_dump()


@router.get("/sources")
def list_knowledge_sources(tenant_id: str = Query(...)):
    sources = manager.source_manager.list_sources(tenant_id)
    return {"sources": [s.model_dump() for s in sources]}


@router.get("/provenance")
def get_provenance_chain(target_id: str = Query(...), tenant_id: str = Query(...)):
    try:
        chain = manager.provenance_manager.get_provenance_chain(target_id, tenant_id)
        return chain.model_dump()
    except CrossTenantKnowledgeAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target not found.")



@router.post("/relationships")
def create_relationship(req: CreateRelationshipRequest, tenant_id: str = Query(...)):
    rel = manager.relationship_manager.create_relationship(
        tenant_id=tenant_id,
        source_id=req.source_id,
        target_id=req.target_id,
        relationship_type=req.relationship_type,
        strength=req.strength,
        evidence_description=req.evidence_description,
    )
    manager.graph_manager.add_edge(tenant_id, rel)
    return rel.model_dump()


@router.get("/relationships")
def list_relationships(tenant_id: str = Query(...), source_id: Optional[str] = None):
    rels = manager.relationship_manager.list_relationships(tenant_id, source_id=source_id)
    return {"relationships": [r.model_dump() for r in rels]}


@router.get("/graph")
def traverse_graph(start_node_id: str = Query(...), tenant_id: str = Query(...), depth: int = Query(2)):
    try:
        trav = manager.graph_manager.traverse(tenant_id, start_node_id, depth=depth)
        return trav.model_dump()
    except CrossTenantKnowledgeAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Node not found.")



@router.post("/retrieval")
def plan_and_retrieve(req: RetrievalApiRequest, tenant_id: str = Query(...)):
    from app.knowledge_intelligence.retrieval import KnowledgeRetrievalRequest, RetrievalConstraint
    ret_req = KnowledgeRetrievalRequest(
        tenant_id=tenant_id,
        query=req.query,
        constraints=RetrievalConstraint(max_classification=req.max_classification),
    )
    candidates = manager.knowledge_manager.list_knowledge(tenant_id)
    res = manager.retrieval_manager.plan_and_retrieve(ret_req, candidates)
    return res.model_dump()


@router.post("/context")
def assemble_context(req: ContextApiRequest, tenant_id: str = Query(...)):
    candidates = []
    for i_id in req.item_ids:
        try:
            candidates.append(manager.knowledge_manager.get_knowledge(i_id, tenant_id))
        except (KnowledgeNotFoundException, CrossTenantKnowledgeAccessException):
            pass
    ctx = manager.context_manager.create_context(tenant_id, candidates, max_items=req.max_items)
    return ctx.model_dump()


@router.get("/contradictions")
def list_contradictions(tenant_id: str = Query(...)):
    cons = manager.contradiction_manager.list_contradictions(tenant_id)
    return {"contradictions": [c.model_dump() for c in cons]}


@router.post("/recommendations")
def create_recommendation(req: CreateRecommendationApiRequest, tenant_id: str = Query(...)):
    rec = manager.recommendation_engine.create_recommendation(
        tenant_id=tenant_id,
        target_id=req.target_id,
        title=req.title,
        rationale=req.rationale,
        is_high_risk=req.is_high_risk,
    )
    return rec.model_dump()


@router.get("/recommendations")
def list_recommendations(tenant_id: str = Query(...)):
    recs = manager.recommendation_engine.list_recommendations(tenant_id)
    return {"recommendations": [r.model_dump() for r in recs]}


@router.post("/memory")
def record_memory(req: RecordMemoryApiRequest, tenant_id: str = Query(...)):
    mem = manager.memory_manager.record_memory(
        tenant_id=tenant_id,
        key=req.key,
        value_summary=req.value_summary,
        reference_id=req.reference_id,
    )
    return mem.model_dump()


@router.get("/memory")
def list_memory(tenant_id: str = Query(...)):
    mems = manager.memory_manager.list_memories(tenant_id)
    return {"memories": [m.model_dump() for m in mems]}


@router.get("/analytics")
def get_analytics_report(tenant_id: str = Query(...)):
    items = manager.knowledge_manager.list_knowledge(tenant_id)
    cons = manager.contradiction_manager.list_contradictions(tenant_id)
    report = manager.analytics_engine.generate_report(tenant_id, total_items=len(items), contradiction_count=len(cons))
    return report.model_dump()
