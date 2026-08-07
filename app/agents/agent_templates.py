"""
Pre-configured Agent Templates
"""

from typing import Dict
from app.agents.agent_config import AgentConfig

AGENT_TEMPLATES: Dict[str, AgentConfig] = {
    "knowledge_assistant": AgentConfig(
        name="Knowledge Assistant",
        description="Searches enterprise knowledge base to answer user queries with verified citations.",
        system_prompt="You are an Enterprise Knowledge Assistant. Search the knowledge base for reliable answers.",
        planner_strategy="react",
        tools=["knowledge_search", "calculator"],
        enable_reflection=True
    ),
    "code_reviewer": AgentConfig(
        name="Code Reviewer",
        description="Analyzes and executes code snippets to evaluate correctness.",
        system_prompt="You are an expert Code Reviewer. Inspect code logic, test execution, and offer improvements.",
        planner_strategy="plan_execute",
        tools=["python_interpreter"],
        require_approval_tools=["shell_executor"]
    ),
    "data_analyst": AgentConfig(
        name="Data Analyst",
        description="Performs analytical reasoning, calculations, and data processing.",
        system_prompt="You are a Data Analyst. Perform step-by-step mathematical reasoning.",
        planner_strategy="tree_of_thought",
        tools=["calculator", "python_interpreter"]
    )
}
