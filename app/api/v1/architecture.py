"""REST API Endpoints for Enterprise AI Architecture & Digital Twin Platform (Phase 5.26)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from app.architecture_platform.change_management import ArchitectureChangeType
from app.architecture_platform.dependencies import DependencyStrength, DependencyType
from app.architecture_platform.exceptions import (
    ArchitectureChangeNotFoundException,
    ArchitectureNodeNotFoundException,
    CrossTenantArchitectureAccessException,
    ImmutableTopologySnapshotException,
)
from app.architecture_platform.manager import ArchitecturePlatformManager
from app.architecture_platform.nodes import ArchitectureNodeType

router = APIRouter(prefix="/v1/architecture", tags=["architecture-platform"])
mgr = ArchitecturePlatformManager()


def _get_tenant_id(x_tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID")) -> str:
    return x_tenant_id or "global"


@router.post("/nodes")
async def create_node(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Register an architecture node."""
    name = payload.get("name", "Unnamed Node")
    node_type = ArchitectureNodeType(payload.get("node_type", "SERVICE"))
    environment = payload.get("environment", "production")
    owner_id = payload.get("owner_id", "system")
    attributes = payload.get("attributes", {})

    node = mgr.discover_and_register_node(
        tenant_id=tenant_id,
        name=name,
        node_type=node_type,
        environment=environment,
        owner_id=owner_id,
        attributes=attributes,
    )
    return node.model_dump()


@router.get("/nodes")
async def list_nodes(
    tenant_id: str = Depends(_get_tenant_id),
    environment: Optional[str] = Query(None),
):
    """List architecture nodes for tenant."""
    nodes = mgr.node_manager.list_nodes(tenant_id=tenant_id, environment=environment)
    return [n.model_dump() for n in nodes]


@router.get("/nodes/{node_id}")
async def get_node(
    node_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get node details."""
    try:
        node = mgr.node_manager.get_node(node_id, tenant_id)
        return node.model_dump()
    except ArchitectureNodeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    except CrossTenantArchitectureAccessException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.message)


@router.post("/dependencies")
async def add_dependency(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Add directed dependency between nodes."""
    src = payload.get("source_node_id")
    tgt = payload.get("target_node_id")
    dep_type = DependencyType(payload.get("dependency_type", "DEPENDS_ON"))
    strength = DependencyStrength(payload.get("strength", "STRONG"))

    if not src or not tgt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="source_node_id and target_node_id are required."
        )

    dep = mgr.add_dependency(
        tenant_id=tenant_id,
        source_node_id=src,
        target_node_id=tgt,
        dependency_type=dep_type,
        strength=strength,
    )
    return dep.model_dump()


@router.get("/topology")
async def get_topology(
    tenant_id: str = Depends(_get_tenant_id),
    environment: str = Query("production"),
):
    """Retrieve tenant topology graph."""
    top = mgr.topology_manager.build_topology(tenant_id=tenant_id, environment=environment)
    return top.model_dump()


@router.post("/snapshots")
async def create_snapshot(
    payload: Dict[str, Any] = {},
    tenant_id: str = Depends(_get_tenant_id),
):
    """Create an immutable architecture topology snapshot."""
    env = payload.get("environment", "production")
    desc = payload.get("description", "Snapshot")
    snap = mgr.topology_manager.create_snapshot(tenant_id=tenant_id, environment=env, description=desc)
    return snap.model_dump()


@router.get("/snapshots/{snapshot_id}")
async def get_snapshot(
    snapshot_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get immutable snapshot details."""
    try:
        snap = mgr.topology_manager.get_snapshot(snapshot_id, tenant_id)
        return snap.model_dump()
    except ImmutableTopologySnapshotException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/changes")
async def propose_change(
    payload: Dict[str, Any],
    tenant_id: str = Depends(_get_tenant_id),
):
    """Propose an architecture change."""
    idempotency_key = payload.get("idempotency_key")
    action_type = ArchitectureChangeType(payload.get("action_type", "MODIFY"))
    target_nodes = payload.get("target_node_ids", [])

    if not idempotency_key:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="idempotency_key is required.")

    res = mgr.propose_and_evaluate_change(
        tenant_id=tenant_id,
        idempotency_key=idempotency_key,
        action_type=action_type,
        target_node_ids=target_nodes,
    )
    return res


@router.get("/changes/{change_id}")
async def get_change(
    change_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get change status."""
    try:
        change = mgr.change_manager.get_change(change_id, tenant_id)
        return change.model_dump()
    except ArchitectureChangeNotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)


@router.post("/changes/{change_id}/delegate")
async def delegate_change(
    change_id: str,
    tenant_id: str = Depends(_get_tenant_id),
):
    """Delegate approved change execution."""
    try:
        change = mgr.delegate_approved_change(change_id, tenant_id)
        return change.model_dump()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/drift")
async def get_drift(
    tenant_id: str = Depends(_get_tenant_id),
):
    """List architecture drift records."""
    drifts = mgr.drift_detector.list_drifts(tenant_id)
    return [d.model_dump() for d in drifts]


@router.get("/trust")
async def get_trust(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get tenant Architecture Trust Score."""
    trust = mgr.trust_engine.get_trust_score(tenant_id)
    return trust.model_dump()


@router.get("/analytics")
async def get_analytics(
    tenant_id: str = Depends(_get_tenant_id),
):
    """Get tenant architecture report & analytics."""
    report = mgr.analytics_engine.generate_report(tenant_id)
    return report.model_dump()
