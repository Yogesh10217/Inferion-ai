"""REST API Router for Phase 5.19 Enterprise Knowledge, Context Engineering & Organizational Intelligence Platform."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.knowledge_platform.conflicts import ConflictResolutionStrategy
from app.knowledge_platform.context import ContextStrategy
from app.knowledge_platform.knowledge import KnowledgeType
from app.knowledge_platform.manager import KnowledgePlatformManager
from app.knowledge_platform.memory import MemoryScope, MemoryType
from app.knowledge_platform.retrieval import RetrievalStrategy

router = APIRouter(prefix="/v1/knowledge_platform", tags=["knowledge_platform"])
_global_manager = KnowledgePlatformManager()


# DTOs
class CreateKnowledgeRequest(BaseModel):
    title: str
    content: str
    knowledge_type: KnowledgeType = KnowledgeType.DOCUMENT
    tenant_id: str = "global"
    classification: str = "INTERNAL"
    source_system: str = "DataFabric"


class RetrieveRequestDTO(BaseModel):
    query: str
    tenant_id: str = "global"
    identity_id: str = "user"
    user_role: str = "viewer"
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    top_k: int = 5


class BuildContextRequestDTO(BaseModel):
    query: str
    tenant_id: str = "global"
    identity_id: str = "user"
    strategy: ContextStrategy = ContextStrategy.RELEVANCE_FIRST
    max_tokens: int = 2048


class StoreMemoryRequestDTO(BaseModel):
    key: str
    value: Any
    memory_type: MemoryType = MemoryType.ORGANIZATIONAL
    scope: MemoryScope = MemoryScope.TENANT
    tenant_id: str = "global"
    owner_agent_id: Optional[str] = None


class GraphQueryRequestDTO(BaseModel):
    start_node_id: str
    max_hops: int = 2
    tenant_id: str = "global"


class ResolveConflictRequestDTO(BaseModel):
    strategy: ConflictResolutionStrategy = ConflictResolutionStrategy.RECENCY


# Endpoints
@router.get("/health")
def get_health():
    return {"status": "HEALTHY", "subsystem": "KnowledgePlatformManager", "version": "5.19.0"}


@router.post("/knowledge", status_code=status.HTTP_201_CREATED)
def create_knowledge(req: CreateKnowledgeRequest):
    item = _global_manager.create_and_index_knowledge(
        title=req.title,
        content=req.content,
        knowledge_type=req.knowledge_type,
        tenant_id=req.tenant_id,
        classification=req.classification,
        source_system=req.source_system,
    )
    return item.model_dump()


@router.get("/knowledge")
def list_knowledge(tenant_id: Optional[str] = Query(None)):
    items = _global_manager.knowledge_manager.list_items(tenant_id=tenant_id)
    return [i.model_dump() for i in items]


@router.get("/knowledge/{item_id}")
def get_knowledge_item(item_id: str):
    try:
        item = _global_manager.knowledge_manager.get_item(item_id)
        return item.model_dump()
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/knowledge/{item_id}/validate")
def validate_knowledge_item(item_id: str):
    try:
        item = _global_manager.knowledge_manager.get_item(item_id)
        res = _global_manager.validation_engine.validate_item(item)
        return res.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/knowledge/{item_id}/versions")
def get_knowledge_versions(item_id: str):
    try:
        item = _global_manager.knowledge_manager.get_item(item_id)
        return [v.model_dump() for v in item.history]
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/retrieve")
def retrieve_knowledge(req: RetrieveRequestDTO):
    try:
        from app.knowledge_platform.retrieval import RetrievalRequest

        r_req = RetrievalRequest(
            query=req.query,
            tenant_id=req.tenant_id,
            identity_id=req.identity_id,
            user_role=req.user_role,
            strategy=req.strategy,
            top_k=req.top_k,
        )
        res = _global_manager.retrieval_pipeline.execute_retrieval(r_req)
        return res.model_dump()
    except Exception as e:
        raise HTTPException(status_code=403 if "DENIED" in str(e) else 400, detail=str(e))


@router.post("/context")
def build_context_window(req: BuildContextRequestDTO):
    from app.knowledge_platform.retrieval import RetrievalRequest

    r_req = RetrievalRequest(query=req.query, tenant_id=req.tenant_id, identity_id=req.identity_id)
    ret_res = _global_manager.retrieval_pipeline.execute_retrieval(r_req)
    cwin = _global_manager.context_builder.build_context(ret_res, strategy=req.strategy, max_tokens=req.max_tokens)
    return cwin.model_dump()


@router.post("/memory", status_code=status.HTTP_201_CREATED)
def store_memory(req: StoreMemoryRequestDTO):
    mem = _global_manager.memory_manager.store_memory(
        key=req.key,
        value=req.value,
        memory_type=req.memory_type,
        scope=req.scope,
        tenant_id=req.tenant_id,
        owner_agent_id=req.owner_agent_id,
    )
    return mem.model_dump()


@router.get("/memory")
def list_memory(tenant_id: Optional[str] = Query(None), scope: Optional[MemoryScope] = Query(None)):
    memories = _global_manager.memory_manager.list_memories(tenant_id=tenant_id, scope=scope)
    return [m.model_dump() for m in memories]


@router.delete("/memory/{memory_id}")
def delete_memory(memory_id: str):
    if memory_id in _global_manager.memory_manager._memories:
        del _global_manager.memory_manager._memories[memory_id]
        return {"status": "DELETED", "memory_id": memory_id}
    raise HTTPException(status_code=404, detail=f"Memory '{memory_id}' not found")


@router.get("/graph")
def get_graph_nodes(tenant_id: Optional[str] = Query(None)):
    nodes = list(_global_manager.knowledge_graph_manager._nodes.values())
    if tenant_id:
        nodes = [n for n in nodes if n.tenant_id == tenant_id]
    return [n.model_dump() for n in nodes]


@router.post("/graph/query")
def query_graph(req: GraphQueryRequestDTO):
    try:
        nodes = _global_manager.knowledge_graph_manager.multi_hop_traversal(
            start_node_id=req.start_node_id,
            max_hops=req.max_hops,
            tenant_id=req.tenant_id,
        )
        return [n.model_dump() for n in nodes]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/access-check")
def access_check(
    identity_id: str, classification: str = "INTERNAL", user_role: str = "viewer", tenant_id: str = "global"
):
    dec = _global_manager.governance_engine.evaluate_access(
        identity_id=identity_id, user_role=user_role, tenant_id=tenant_id, classification=classification
    )
    return dec.model_dump()


@router.get("/conflicts")
def list_conflicts(tenant_id: Optional[str] = Query(None)):
    conflicts = _global_manager.conflict_manager.list_conflicts(tenant_id=tenant_id)
    return [c.model_dump() for c in conflicts]


@router.post("/conflicts/{conflict_id}/resolve")
def resolve_conflict(conflict_id: str, req: ResolveConflictRequestDTO):
    try:
        cnflct = _global_manager.conflict_manager.resolve_conflict(conflict_id, strategy=req.strategy)
        return cnflct.model_dump()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/analytics")
def get_analytics(tenant_id: str = "global"):
    insight = _global_manager.analytics_engine.generate_insight(tenant_id=tenant_id)
    return insight.model_dump()
