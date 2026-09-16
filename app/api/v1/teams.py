"""
FastAPI Router for Enterprise Multi-Agent Collaboration Platform (/v1/teams)
"""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.multi_agent.agent_coordinator import MultiAgentCoordinator
from app.multi_agent.agent_profile import AgentProfile
from app.multi_agent.agent_role import AgentRole, RoleType
from app.multi_agent.agent_team import AgentTeam, TeamExecutionContext, TeamType
from app.multi_agent.exceptions import RolePermissionDenied

router = APIRouter(prefix="/v1/teams", tags=["teams"])

# Shared registry of Agent Teams
_teams_store: Dict[str, AgentTeam] = {}
_global_coordinator = MultiAgentCoordinator()

# Pre-register default preset team
_preset_team = AgentTeam.create_preset_team(TeamType.ENGINEERING, "Default Dev Team", tenant_id="global")
_teams_store[_preset_team.team_id] = _preset_team


def get_coordinator() -> MultiAgentCoordinator:
    return _global_coordinator


class TeamCreateSchema(BaseModel):
    name: str
    team_type: str = "custom"
    description: str = ""
    tenant_id: str = "global"
    budget_dollars: float = 10.0


class MemberAddSchema(BaseModel):
    name: str
    role: str = "executor"
    system_prompt: str = "You are a specialized agent."


class TeamRunSchema(BaseModel):
    goal: str
    inputs: Dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = "global"


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_team(data: TeamCreateSchema):
    """Create a new agent team."""
    ttype = TeamType(data.team_type) if data.team_type in [t.value for t in TeamType] else TeamType.CUSTOM
    team = AgentTeam.create_preset_team(ttype, name=data.name, tenant_id=data.tenant_id)
    team.config.budget_dollars = data.budget_dollars
    team.config.description = data.description
    _teams_store[team.team_id] = team
    return {"status": "created", "team_id": team.team_id, "name": team.name if hasattr(team, "name") else data.name}


@router.get("")
async def list_teams(tenant_id: str = "global"):
    """List all registered agent teams."""
    teams = [t for t in _teams_store.values() if t.config.tenant_id in (tenant_id, "global", "default_tenant")]
    return {"teams": [{"team_id": t.team_id, "name": t.config.name, "type": t.config.team_type.value, "members_count": len(t.members)} for t in teams]}


@router.get("/{id}")
async def get_team(id: str):
    """Get agent team details by ID."""
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    team = _teams_store[id]
    return {
        "team_id": team.team_id,
        "name": team.config.name,
        "type": team.config.team_type.value,
        "status": team.status,
        "members": [m.model_dump() for m in team.list_members()],
    }


@router.patch("/{id}")
async def update_team(id: str, description: Optional[str] = None, budget_dollars: Optional[float] = None):
    """Update team configuration."""
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    team = _teams_store[id]
    if description:
        team.config.description = description
    if budget_dollars is not None:
        team.config.budget_dollars = budget_dollars
    return {"status": "updated", "team_id": id}


@router.delete("/{id}")
async def delete_team(id: str):
    """Delete an agent team by ID."""
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    del _teams_store[id]
    return {"status": "deleted", "team_id": id}


@router.post("/{id}/run")
async def run_team(
    id: str,
    data: TeamRunSchema,
    coordinator: MultiAgentCoordinator = Depends(get_coordinator),
):
    """Execute autonomous team run for a given goal."""
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    team = _teams_store[id]
    ctx = TeamExecutionContext(team_id=id, goal=data.goal, tenant_id=data.tenant_id, initial_inputs=data.inputs)

    try:
        res = await coordinator.execute_team_run(team, ctx)
        return {"result": res}
    except RolePermissionDenied as rpe:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(rpe))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{id}/pause")
async def pause_team(id: str, coordinator: MultiAgentCoordinator = Depends(get_coordinator)):
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    st = coordinator.lifecycle_manager.pause(id)
    return {"status": st.value, "team_id": id}


@router.post("/{id}/resume")
async def resume_team(id: str, coordinator: MultiAgentCoordinator = Depends(get_coordinator)):
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    st = coordinator.lifecycle_manager.resume(id)
    return {"status": st.value, "team_id": id}


@router.post("/{id}/cancel")
async def cancel_team(id: str, coordinator: MultiAgentCoordinator = Depends(get_coordinator)):
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    st = coordinator.lifecycle_manager.cancel(id)
    return {"status": st.value, "team_id": id}


@router.get("/{id}/members")
async def get_team_members(id: str):
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    team = _teams_store[id]
    return {"team_id": id, "members": [m.model_dump() for m in team.list_members()]}


@router.post("/{id}/members")
async def add_team_member(id: str, data: MemberAddSchema):
    if id not in _teams_store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Team '{id}' not found")
    team = _teams_store[id]
    rtype = RoleType(data.role) if data.role in [r.value for r in RoleType] else RoleType.EXECUTOR
    prof = AgentProfile(name=data.name, role=AgentRole.get_preset_role(rtype), system_prompt=data.system_prompt)
    mbr = team.add_member(prof)
    return {"status": "added", "member": mbr.model_dump()}


@router.get("/{id}/messages")
async def get_team_messages(id: str, coordinator: MultiAgentCoordinator = Depends(get_coordinator)):
    msgs = coordinator.message_bus.get_team_history(id)
    return {"team_id": id, "messages": [m.model_dump() for m in msgs]}


@router.get("/{id}/history")
async def get_team_history(id: str, coordinator: MultiAgentCoordinator = Depends(get_coordinator)):
    entries = coordinator.blackboard.list_entries(team_id=id)
    return {"team_id": id, "history": [e.model_dump() for e in entries]}


@router.get("/{id}/metrics")
async def get_team_metrics(id: str, coordinator: MultiAgentCoordinator = Depends(get_coordinator)):
    summary = coordinator.billing_tracker.get_team_billing_summary(id)
    return {"team_id": id, "metrics": summary}


@router.get("/{id}/billing")
async def get_team_billing(id: str, coordinator: MultiAgentCoordinator = Depends(get_coordinator)):
    summary = coordinator.billing_tracker.get_team_billing_summary(id)
    return {"team_id": id, "billing": summary}
