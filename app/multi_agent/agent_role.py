"""
Agent Roles Definition Layer
"""

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class RoleType(str, Enum):
    MANAGER = "manager"
    PLANNER = "planner"
    RESEARCHER = "researcher"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    QA = "qa"
    ANALYST = "analyst"
    EXECUTOR = "executor"
    TOOL_SPECIALIST = "tool_specialist"
    MEMORY_SPECIALIST = "memory_specialist"
    COMPLIANCE_OFFICER = "compliance_officer"
    CUSTOM = "custom"


class AgentRole(BaseModel):
    """Defines capabilities, permissions, delegation rules, and limits for an Agent Role."""
    role_type: RoleType = RoleType.EXECUTOR
    name: str = "Executor"
    description: str = "Standard Execution Agent Role"
    capabilities: List[str] = Field(default_factory=lambda: ["execute_task"])
    permissions: List[str] = Field(default_factory=lambda: ["tools:execute", "memory:read"])
    delegation_policies: List[str] = Field(default_factory=lambda: ["delegate_by_capability"])
    escalation_rules: List[str] = Field(default_factory=lambda: ["escalate_on_failure"])
    max_concurrent_tasks: int = 5
    cost_limit_per_task: float = 1.0

    @staticmethod
    def get_preset_role(role_type: RoleType) -> "AgentRole":
        presets = {
            RoleType.MANAGER: AgentRole(
                role_type=RoleType.MANAGER,
                name="Team Manager",
                description="Manages team goals, delegates sub-tasks, and supervises execution",
                capabilities=["delegate_task", "approve_action", "evaluate_results"],
                permissions=["team:manage", "team:run", "tools:execute", "memory:read", "memory:write"],
                max_concurrent_tasks=10,
            ),
            RoleType.PLANNER: AgentRole(
                role_type=RoleType.PLANNER,
                name="Planner",
                description="Breaks down complex goals into DAG plans and agent roles",
                capabilities=["create_plan", "decompose_goal"],
                permissions=["tools:execute", "memory:read"],
            ),
            RoleType.RESEARCHER: AgentRole(
                role_type=RoleType.RESEARCHER,
                name="Researcher",
                description="Gathers knowledge, searches web/RAG, and extracts facts",
                capabilities=["search_knowledge", "retrieve_info", "web_search"],
                permissions=["knowledge:read", "tools:execute"],
            ),
            RoleType.DEVELOPER: AgentRole(
                role_type=RoleType.DEVELOPER,
                name="Developer",
                description="Writes code, executes python tools, builds software features",
                capabilities=["write_code", "python_sandbox", "git_operations"],
                permissions=["tools:execute", "memory:read", "memory:write"],
            ),
            RoleType.REVIEWER: AgentRole(
                role_type=RoleType.REVIEWER,
                name="Code & Content Reviewer",
                description="Reviews code, validates security, checks compliance",
                capabilities=["code_review", "security_check"],
                permissions=["tools:execute", "memory:read"],
            ),
            RoleType.QA: AgentRole(
                role_type=RoleType.QA,
                name="QA & Verification Specialist",
                description="Executes test cases, verifies outputs, reports bugs",
                capabilities=["test_execution", "bug_reporting"],
                permissions=["tools:execute"],
            ),
            RoleType.ANALYST: AgentRole(
                role_type=RoleType.ANALYST,
                name="Data Analyst",
                description="Analyzes structured data, runs SQL queries, outputs metrics",
                capabilities=["sql_query", "data_analysis"],
                permissions=["tools:execute", "memory:read"],
            ),
            RoleType.EXECUTOR: AgentRole(
                role_type=RoleType.EXECUTOR,
                name="General Executor",
                description="Executes assigned sub-tasks",
                capabilities=["execute_task"],
                permissions=["tools:execute"],
            ),
            RoleType.TOOL_SPECIALIST: AgentRole(
                role_type=RoleType.TOOL_SPECIALIST,
                name="Tool Specialist",
                description="Interacts with external API tools and integrations",
                capabilities=["api_call", "integration_exec"],
                permissions=["tools:execute"],
            ),
            RoleType.MEMORY_SPECIALIST: AgentRole(
                role_type=RoleType.MEMORY_SPECIALIST,
                name="Memory Specialist",
                description="Manages episodic, semantic, and working memories across team",
                capabilities=["manage_memory", "semantic_search"],
                permissions=["memory:read", "memory:write", "memory:delete"],
            ),
            RoleType.COMPLIANCE_OFFICER: AgentRole(
                role_type=RoleType.COMPLIANCE_OFFICER,
                name="Compliance Officer",
                description="Enforces governance rules, RBAC, cost limits, and security policies",
                capabilities=["audit_validation", "enforce_policy"],
                permissions=["admin:read", "audit:read"],
            ),
        }
        return presets.get(role_type, AgentRole(role_type=role_type, name=role_type.value))
