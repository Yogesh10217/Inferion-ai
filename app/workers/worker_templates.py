"""
Digital Worker Templates
"""

from enum import Enum

from pydantic import BaseModel, Field


class WorkerTemplateType(str, Enum):
    RESEARCH = "research"
    SUPPORT = "support"
    ENGINEERING = "engineering"
    DEVOPS = "devops"
    COMPLIANCE = "compliance"
    ANALYST = "analyst"
    CUSTOM = "custom"


class WorkerTemplate(BaseModel):
    template_type: WorkerTemplateType
    name: str
    description: str
    capabilities: list[str] = Field(default_factory=list)
    system_prompt: str = ""

    @staticmethod
    def get_preset(template_type: WorkerTemplateType) -> "WorkerTemplate":
        presets = {
            WorkerTemplateType.RESEARCH: WorkerTemplate(
                template_type=WorkerTemplateType.RESEARCH,
                name="Autonomous Research Worker",
                description="Gathers domain knowledge, queries web/RAG, synthesizes reports",
                capabilities=["knowledge_query", "web_search", "summarization"],
                system_prompt="You are an autonomous research worker.",
            ),
            WorkerTemplateType.ENGINEERING: WorkerTemplate(
                template_type=WorkerTemplateType.ENGINEERING,
                name="Autonomous Engineering Worker",
                description="Writes code, creates pull requests, runs unit tests",
                capabilities=["code_writing", "git_ops", "python_sandbox"],
                system_prompt="You are an autonomous engineering worker.",
            ),
            WorkerTemplateType.DEVOPS: WorkerTemplate(
                template_type=WorkerTemplateType.DEVOPS,
                name="Autonomous DevOps Worker",
                description="Monitors platform deployments, manages infra scripts",
                capabilities=["shell_exec", "metrics_monitoring"],
                system_prompt="You are an autonomous DevOps worker.",
            ),
            WorkerTemplateType.SUPPORT: WorkerTemplate(
                template_type=WorkerTemplateType.SUPPORT,
                name="Autonomous Support Worker",
                description="Handles customer tickets, queries knowledge base",
                capabilities=["ticket_response", "memory_query"],
                system_prompt="You are an autonomous support worker.",
            ),
            WorkerTemplateType.COMPLIANCE: WorkerTemplate(
                template_type=WorkerTemplateType.COMPLIANCE,
                name="Autonomous Compliance Worker",
                description="Audits security logs, validates RBAC and tenant boundaries",
                capabilities=["audit_log_analysis", "compliance_validation"],
                system_prompt="You are an autonomous compliance worker.",
            ),
            WorkerTemplateType.ANALYST: WorkerTemplate(
                template_type=WorkerTemplateType.ANALYST,
                name="Autonomous Data Analyst Worker",
                description="Runs SQL queries, generates metric dashboards",
                capabilities=["sql_query", "metrics_analysis"],
                system_prompt="You are an autonomous data analyst worker.",
            ),
        }
        return presets.get(
            template_type,
            WorkerTemplate(template_type=template_type, name=template_type.value, description="Custom worker"),
        )
