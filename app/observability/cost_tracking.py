"""AI Cost & Token Observability subsystem."""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from app.observability.context import ObservabilityContext, get_current_context

logger = logging.getLogger(__name__)

# Standard fallback rates per 1,000 tokens if pricing rules aren't in DB
DEFAULT_PRICING_TABLE: Dict[str, Dict[str, float]] = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "gemini-1.5-pro": {"input": 0.0035, "output": 0.0105},
    "default": {"input": 0.002, "output": 0.004},
}


@dataclass
class UsageRecord:
    """Represents a single token and cost usage record."""

    execution_id: str
    tenant_id: str
    workspace_id: str
    organization_id: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    model: str
    provider: str
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    tool_name: Optional[str] = None
    team_id: Optional[str] = None
    worker_id: Optional[str] = None
    planning_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CostTracker:
    """Tracks token usage and computes financial cost attribution across enterprise dimensions."""

    def __init__(self, pricing_service: Optional[Any] = None) -> None:
        self.pricing_service = pricing_service
        self._records: List[UsageRecord] = []

    def calculate_cost(
        self,
        model: str,
        provider: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Calculate financial cost based on token counts and model pricing."""
        key = model.lower()
        pricing = DEFAULT_PRICING_TABLE.get(key, DEFAULT_PRICING_TABLE["default"])
        input_cost = (input_tokens / 1000.0) * pricing["input"]
        output_cost = (output_tokens / 1000.0) * pricing["output"]
        return round(input_cost + output_cost, 6)

    def record_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "default",
        provider: str = "default",
        context: Optional[ObservabilityContext] = None,
        agent_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        team_id: Optional[str] = None,
        worker_id: Optional[str] = None,
        planning_id: Optional[str] = None,
    ) -> UsageRecord:
        """Record usage and compute cost using active or given context."""
        ctx = context or get_current_context()
        total_tokens = input_tokens + output_tokens
        cost = self.calculate_cost(model, provider, input_tokens, output_tokens)

        record = UsageRecord(
            execution_id=ctx.execution_id or ctx.trace_id,
            tenant_id=ctx.tenant_id or "default",
            workspace_id=ctx.workspace_id or "default",
            organization_id=ctx.organization_id or "default",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            cost=cost,
            model=model,
            provider=provider,
            agent_id=agent_id or ctx.agent_id,
            workflow_id=workflow_id or ctx.workflow_id,
            tool_name=tool_name or ctx.tool_execution_id,
            team_id=team_id or ctx.team_id,
            worker_id=worker_id or ctx.worker_id,
            planning_id=planning_id,
        )

        self._records.append(record)
        return record

    def get_execution_cost(self, execution_id: str) -> Dict[str, Any]:
        """Aggregate total token usage and cost for an execution ID."""
        matching = [r for r in self._records if r.execution_id == execution_id]
        total_cost = sum(r.cost for r in matching)
        input_tokens = sum(r.input_tokens for r in matching)
        output_tokens = sum(r.output_tokens for r in matching)
        total_tokens = sum(r.total_tokens for r in matching)

        return {
            "execution_id": execution_id,
            "cost": round(total_cost, 6),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "records_count": len(matching),
        }

    def get_agent_cost(self, agent_id: str) -> Dict[str, Any]:
        """Aggregate usage and cost for a specific agent."""
        matching = [r for r in self._records if r.agent_id == agent_id]
        return {
            "agent_id": agent_id,
            "cost": round(sum(r.cost for r in matching), 6),
            "total_tokens": sum(r.total_tokens for r in matching),
            "records_count": len(matching),
        }

    def get_workflow_cost(self, workflow_id: str) -> Dict[str, Any]:
        """Aggregate usage and cost for a specific workflow."""
        matching = [r for r in self._records if r.workflow_id == workflow_id]
        return {
            "workflow_id": workflow_id,
            "cost": round(sum(r.cost for r in matching), 6),
            "total_tokens": sum(r.total_tokens for r in matching),
            "records_count": len(matching),
        }

    def get_tenant_cost(self, tenant_id: str) -> Dict[str, Any]:
        """Aggregate usage and cost for a tenant."""
        matching = [r for r in self._records if r.tenant_id == tenant_id]
        return {
            "tenant_id": tenant_id,
            "cost": round(sum(r.cost for r in matching), 6),
            "total_tokens": sum(r.total_tokens for r in matching),
            "records_count": len(matching),
        }

    def get_workspace_cost(self, workspace_id: str) -> Dict[str, Any]:
        """Aggregate usage and cost for a workspace."""
        matching = [r for r in self._records if r.workspace_id == workspace_id]
        return {
            "workspace_id": workspace_id,
            "cost": round(sum(r.cost for r in matching), 6),
            "total_tokens": sum(r.total_tokens for r in matching),
            "records_count": len(matching),
        }

    def get_cost_breakdown(
        self,
        tenant_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Construct multi-level cost attribution hierarchy: Organization -> Tenant -> Workspace -> Execution -> Components."""
        records = self._records
        if tenant_id:
            records = [r for r in records if r.tenant_id == tenant_id]
        if workspace_id:
            records = [r for r in records if r.workspace_id == workspace_id]

        by_org: Dict[str, Dict[str, Any]] = {}
        for r in records:
            org = r.organization_id
            ten = r.tenant_id
            ws = r.workspace_id
            ex = r.execution_id

            if org not in by_org:
                by_org[org] = {"total_cost": 0.0, "tenants": {}}

            org_node = by_org[org]
            org_node["total_cost"] += r.cost

            if ten not in org_node["tenants"]:
                org_node["tenants"][ten] = {"total_cost": 0.0, "workspaces": {}}

            ten_node = org_node["tenants"][ten]
            ten_node["total_cost"] += r.cost

            if ws not in ten_node["workspaces"]:
                ten_node["workspaces"][ws] = {"total_cost": 0.0, "executions": {}}

            ws_node = ten_node["workspaces"][ws]
            ws_node["total_cost"] += r.cost

            if ex not in ws_node["executions"]:
                ws_node["executions"][ex] = {
                    "total_cost": 0.0,
                    "agents": {},
                    "workflows": {},
                    "models": {},
                    "tools": {},
                }

            ex_node = ws_node["executions"][ex]
            ex_node["total_cost"] += r.cost

            if r.agent_id:
                ex_node["agents"][r.agent_id] = ex_node["agents"].get(r.agent_id, 0.0) + r.cost
            if r.workflow_id:
                ex_node["workflows"][r.workflow_id] = ex_node["workflows"].get(r.workflow_id, 0.0) + r.cost
            if r.model:
                ex_node["models"][r.model] = ex_node["models"].get(r.model, 0.0) + r.cost
            if r.tool_name:
                ex_node["tools"][r.tool_name] = ex_node["tools"].get(r.tool_name, 0.0) + r.cost

        # Round all cost values
        for org_data in by_org.values():
            org_data["total_cost"] = round(org_data["total_cost"], 6)
            for ten_data in org_data["tenants"].values():
                ten_data["total_cost"] = round(ten_data["total_cost"], 6)
                for ws_data in ten_data["workspaces"].values():
                    ws_data["total_cost"] = round(ws_data["total_cost"], 6)
                    for ex_data in ws_data["executions"].values():
                        ex_data["total_cost"] = round(ex_data["total_cost"], 6)

        return {
            "total_cost": round(sum(r.cost for r in records), 6),
            "total_tokens": sum(r.total_tokens for r in records),
            "records_count": len(records),
            "hierarchy": by_org,
        }
