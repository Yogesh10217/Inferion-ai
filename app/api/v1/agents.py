"""
Agent Subsystem REST API Router (/v1/agents)
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, Field

from app.agents.agent_context import AgentContext
from app.agents.agent_manager import AgentManager
from app.agents.exceptions import AgentNotFoundError, ApprovalRequiredException, BudgetExceededException, ToolError

router = APIRouter(prefix="/v1/agents", tags=["Agents"])

# Shared global manager instance
_agent_manager = AgentManager()


class CreateAgentRequest(BaseModel):
    id: str
    name: str
    description: str
    system_prompt: str
    model: str = "gpt-4o-mini"
    planner_strategy: str = "react"
    reflection_strategy: str = "self_critique"
    tools: List[str] = Field(default_factory=list)
    max_iterations: int = 15
    max_cost_dollars: Optional[float] = None
    max_tokens: Optional[int] = None
    require_approval_tools: List[str] = Field(default_factory=list)


class RunAgentRequest(BaseModel):
    prompt: str


class ApprovalDecisionRequest(BaseModel):
    approved: bool
    feedback: Optional[str] = None


def get_agent_context(
    x_organization_id: str = Header(default="default_org", alias="X-Organization-Id"),
    x_workspace_id: Optional[str] = Header(default="default_workspace", alias="X-Workspace-Id")
) -> AgentContext:
    return AgentContext(
        organization_id=x_organization_id,
        workspace_id=x_workspace_id
    )


@router.post("", response_model=Dict[str, Any])
async def create_agent(req: CreateAgentRequest):
    config = _agent_manager.create_agent(req.id, req.model_dump())
    return {"status": "success", "agent_id": req.id, "config": config.model_dump()}


@router.get("", response_model=List[Dict[str, Any]])
async def list_agents():
    agents = _agent_manager.registry.list_agents()
    return [{"id": k, "config": v.model_dump()} for k, v in agents.items()]


@router.get("/{agent_id}", response_model=Dict[str, Any])
async def get_agent(agent_id: str):
    try:
        config = _agent_manager.registry.get_agent(agent_id)
        return {"id": agent_id, "config": config.model_dump()}
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{agent_id}", response_model=Dict[str, Any])
async def delete_agent(agent_id: str):
    _agent_manager.registry.delete_agent(agent_id)
    return {"status": "success", "message": f"Agent '{agent_id}' deleted"}


@router.post("/{agent_id}/run", response_model=Dict[str, Any])
async def run_agent(
    agent_id: str,
    req: RunAgentRequest,
    context: AgentContext = Depends(get_agent_context)
):
    try:
        state = await _agent_manager.run_agent(agent_id, req.prompt, context)
        return {"status": "success", "session": state.model_dump()}
    except AgentNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (BudgetExceededException, ToolError, ApprovalRequiredException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent execution error: {e}")


@router.post("/sessions/{session_id}/resume", response_model=Dict[str, Any])
async def resume_session(
    session_id: str,
    approval: Optional[ApprovalDecisionRequest] = None,
    context: AgentContext = Depends(get_agent_context)
):
    try:
        app_dec = approval.approved if approval else None
        state = await _agent_manager.resume_session(session_id, approval_decision=app_dec, context=context)
        return {"status": "success", "session": state.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/sessions/{session_id}/cancel", response_model=Dict[str, Any])
async def cancel_session(
    session_id: str,
    context: AgentContext = Depends(get_agent_context)
):
    try:
        state = await _agent_manager.cancel_session(session_id, context=context)
        return {"status": "success", "session": state.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{agent_id}/sessions", response_model=List[Dict[str, Any]])
async def list_agent_sessions(agent_id: str):
    sessions = _agent_manager.session_manager.list_sessions(agent_id=agent_id)
    return [s.model_dump() for s in sessions]
