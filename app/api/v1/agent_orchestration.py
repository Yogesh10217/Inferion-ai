"""REST API Router for Enterprise AI Agent Orchestration Platform (Phase 5.36)."""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.agent_orchestration.agents import AgentRole, AgentType
from app.agent_orchestration.collaboration import AgentParticipant, CollaborationType
from app.agent_orchestration.exceptions import (
    AgentAutonomyViolationException,
    AgentCapabilityViolationException,
    AgentNotFoundException,
    AgentToolAccessDeniedException,
    CrossTenantAgentAccessException,
    HighRiskAgentActionRequiresApprovalException,
)
from app.agent_orchestration.manager import AgentOrchestrationManager
from app.agent_orchestration.tasks import AgentTaskPriority, AgentTaskType

router = APIRouter(prefix="/v1/agents", tags=["Agent Orchestration"])
manager = AgentOrchestrationManager()


class RegisterAgentRequest(BaseModel):
    name: str
    agent_type: AgentType = AgentType.GENERAL
    role: AgentRole = AgentRole.TASK_EXECUTOR
    capabilities: List[str] = Field(default_factory=list)
    autonomy_policy_id: Optional[str] = None
    description: str = ""


class CreateTaskApiRequest(BaseModel):
    agent_id: str
    goal: str
    prompt: str
    task_type: AgentTaskType = AgentTaskType.EXECUTION
    priority: AgentTaskPriority = AgentTaskPriority.MEDIUM
    target_systems: List[str] = Field(default_factory=list)


class ExecuteTaskApiRequest(BaseModel):
    goal: str
    prompt: str
    agent_id: Optional[str] = None
    task_type: AgentTaskType = AgentTaskType.EXECUTION
    priority: AgentTaskPriority = AgentTaskPriority.MEDIUM
    target_systems: List[str] = Field(default_factory=list)
    is_destructive: bool = False
    estimated_cost: float = 0.05


class CreateCollaborationApiRequest(BaseModel):
    collaboration_type: CollaborationType = CollaborationType.SUPERVISOR_WORKER
    participants: List[AgentParticipant]


@router.post("/register")
def register_agent(req: RegisterAgentRequest, tenant_id: str = Query(...)):
    agent = manager.agent_manager.register_agent(
        tenant_id=tenant_id,
        name=req.name,
        agent_type=req.agent_type,
        role=req.role,
        capabilities=req.capabilities,
        autonomy_policy_id=req.autonomy_policy_id,
        description=req.description,
    )
    return agent.model_dump()


@router.get("")
def list_agents(tenant_id: str = Query(...), agent_type: Optional[AgentType] = None):
    agents = manager.agent_manager.list_agents(tenant_id, agent_type=agent_type)
    return {"agents": [a.model_dump() for a in agents]}


@router.get("/{agent_id}")
def get_agent(agent_id: str, tenant_id: str = Query(...)):
    try:
        agent = manager.agent_manager.get_agent(agent_id, tenant_id)
        return agent.model_dump()
    except CrossTenantAgentAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent resource not found or access denied.")
    except AgentNotFoundException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Agent '{agent_id}' not found.")


@router.post("/tasks")
def create_task(req: CreateTaskApiRequest, tenant_id: str = Query(...)):
    try:
        task = manager.task_manager.create_task(
            tenant_id=tenant_id,
            agent_id=req.agent_id,
            goal=req.goal,
            prompt=req.prompt,
            task_type=req.task_type,
            priority=req.priority,
            target_systems=req.target_systems,
        )
        return task.model_dump()
    except CrossTenantAgentAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found or access denied.")


@router.get("/tasks")
def list_tasks(tenant_id: str = Query(...), agent_id: Optional[str] = None):
    tasks = manager.task_manager.list_tasks(tenant_id, agent_id=agent_id)
    return {"tasks": [t.model_dump() for t in tasks]}


@router.post("/execute")
def execute_task(req: ExecuteTaskApiRequest, tenant_id: str = Query(...)):
    try:
        res = manager.run_full_agent_task_lifecycle(
            tenant_id=tenant_id,
            goal=req.goal,
            prompt=req.prompt,
            agent_id=req.agent_id,
            task_type=req.task_type,
            priority=req.priority,
            target_systems=req.target_systems,
            is_destructive=req.is_destructive,
            estimated_cost=req.estimated_cost,
        )
        return res
    except CrossTenantAgentAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found or access denied.")
    except HighRiskAgentActionRequiresApprovalException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (AgentAutonomyViolationException, AgentCapabilityViolationException, AgentToolAccessDeniedException) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/collaborations")
def create_collaboration(req: CreateCollaborationApiRequest, tenant_id: str = Query(...)):
    try:
        session = manager.collaboration_manager.create_session(
            tenant_id=tenant_id,
            collaboration_type=req.collaboration_type,
            participants=req.participants,
        )
        return session.model_dump()
    except CrossTenantAgentAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cross-tenant collaboration is prohibited.")


@router.get("/traces/{trace_id}")
def get_trace(trace_id: str, tenant_id: str = Query(...)):
    try:
        trace = manager.trace_manager.get_trace(trace_id, tenant_id)
        return trace.model_dump()
    except CrossTenantAgentAccessException:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trace not found or access denied.")


@router.get("/analytics")
def get_analytics(tenant_id: str = Query(...)):
    report = manager.analytics_engine.generate_report(tenant_id)
    return report.model_dump()


@router.get("/summary")
def get_summary(tenant_id: str = Query(...)):
    return manager.get_platform_summary(tenant_id)
