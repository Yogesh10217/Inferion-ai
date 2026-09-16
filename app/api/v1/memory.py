"""
Enterprise Memory Subsystem REST API Router (/v1/memory)
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel

from app.memory.exceptions import MemoryNotFoundError, TenantMemoryIsolationError
from app.memory.memory_manager import MemoryManager

router = APIRouter(prefix="/v1/memory", tags=["Memory"])

_memory_manager = MemoryManager()


class CreateMemoryRequest(BaseModel):
    content: str
    context_hint: Optional[str] = None
    user_id: Optional[str] = None


class SearchMemoryRequest(BaseModel):
    query: str
    top_k: int = 10


class CompressMemoryRequest(BaseModel):
    session_id: str
    max_tokens: int = 2048


class SummarizeMemoryRequest(BaseModel):
    text: str
    max_words: int = 100


class ProfileUpdateRequest(BaseModel):
    profile_data: Dict[str, Any]


def get_tenant_context(
    x_organization_id: str = Header(default="default_org", alias="X-Organization-Id"),
    x_workspace_id: Optional[str] = Header(default="default_workspace", alias="X-Workspace-Id"),
) -> Dict[str, str]:
    return {
        "organization_id": x_organization_id,
        "workspace_id": x_workspace_id or "default_workspace",
    }


@router.post("", response_model=Dict[str, Any])
async def create_memory(
    req: CreateMemoryRequest,
    tenant: Dict[str, str] = Depends(get_tenant_context),
):
    rec = _memory_manager.create_memory(
        content=req.content,
        organization_id=tenant["organization_id"],
        workspace_id=tenant["workspace_id"],
        user_id=req.user_id,
        context_hint=req.context_hint,
    )
    return {"status": "success", "memory": rec.to_dict()}


@router.get("", response_model=List[Dict[str, Any]])
async def list_memories(
    memory_type: Optional[str] = None,
    tenant: Dict[str, str] = Depends(get_tenant_context),
):
    memories = _memory_manager.list_memories(
        organization_id=tenant["organization_id"],
        workspace_id=tenant["workspace_id"],
        memory_type=memory_type,
    )
    return [m.to_dict() for m in memories]


@router.get("/profile", response_model=Dict[str, Any])
async def get_profile(user_id: str = "default_user"):
    return {"user_id": user_id, "profile": _memory_manager.get_profile(user_id)}


@router.patch("/profile", response_model=Dict[str, Any])
async def update_profile(req: ProfileUpdateRequest, user_id: str = "default_user"):
    updated = _memory_manager.update_profile(user_id, req.profile_data)
    return {"status": "success", "profile": updated}


@router.get("/analytics", response_model=Dict[str, Any])
async def get_analytics():
    return _memory_manager.get_analytics()


@router.get("/{memory_id}", response_model=Dict[str, Any])
async def get_memory(
    memory_id: str,
    tenant: Dict[str, str] = Depends(get_tenant_context),
):
    try:
        rec = _memory_manager.get_memory(memory_id, organization_id=tenant["organization_id"])
        return {"memory": rec.to_dict()}
    except MemoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except TenantMemoryIsolationError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{memory_id}", response_model=Dict[str, Any])
async def delete_memory(
    memory_id: str,
    tenant: Dict[str, str] = Depends(get_tenant_context),
):
    try:
        _memory_manager.delete_memory(memory_id, organization_id=tenant["organization_id"])
        return {"status": "success", "message": f"Memory '{memory_id}' deleted"}
    except MemoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/search", response_model=List[Dict[str, Any]])
async def search_memory(
    req: SearchMemoryRequest,
    tenant: Dict[str, str] = Depends(get_tenant_context),
):
    results = _memory_manager.search_memories(
        query=req.query,
        organization_id=tenant["organization_id"],
        top_k=req.top_k,
    )
    return [r.to_dict() for r in results]


@router.post("/compress", response_model=Dict[str, Any])
async def compress_memory(req: CompressMemoryRequest):
    conv = _memory_manager.service.get_conversation_memory(req.session_id)
    compressed = conv.compress()
    return {"status": "success", "compressed": compressed}


@router.post("/summarize", response_model=Dict[str, Any])
async def summarize_memory(req: SummarizeMemoryRequest):
    summary = await _memory_manager.service.summarizer.summarize_text(req.text, max_words=req.max_words)
    return {"status": "success", "summary": summary}


@router.post("/archive", response_model=Dict[str, Any])
async def archive_memory(
    memory_id: str,
    tenant: Dict[str, str] = Depends(get_tenant_context),
):
    try:
        rec = _memory_manager.archive_memory(memory_id, organization_id=tenant["organization_id"])
        return {"status": "success", "memory": rec.to_dict()}
    except MemoryNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
