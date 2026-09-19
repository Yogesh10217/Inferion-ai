"""
Built-in Core Agent Tools (Knowledge, Web, Math, System)
"""

import logging
import math
from typing import Any, Dict

from app.agents.agent_context import AgentContext
from app.agents.knowledge_adapter import KnowledgeAdapter
from app.agents.tools.schemas import ToolDefinition, ToolParameter

logger = logging.getLogger(__name__)

_knowledge_adapter = KnowledgeAdapter()


async def execute_knowledge_search(query: str, context: AgentContext, top_k: int = 3) -> Dict[str, Any]:
    return await _knowledge_adapter.search_and_build_context(query, context, top_k=top_k)


async def execute_calculator(expression: str, context: AgentContext) -> Dict[str, Any]:
    # Safe evaluation of basic math expressions
    allowed_names = {"math": math, "abs": abs, "round": round, "min": min, "max": max, "pow": pow}
    code = compile(expression, "<string>", "eval")
    for name in code.co_names:
        if name not in allowed_names:
            raise ValueError(f"Use of name '{name}' is not allowed in calculator")
    result = eval(code, {"__builtins__": {}}, allowed_names)  # nosec B307
    return {"expression": expression, "result": result}


BUILTIN_TOOLS = {
    "knowledge_search": {
        "definition": ToolDefinition(
            name="knowledge_search",
            description="Searches Phase 5.0 Knowledge Base for context & documents",
            parameters=[
                ToolParameter(name="query", type="string", description="Search query string"),
                ToolParameter(name="top_k", type="integer", description="Number of results", required=False, default=3),
            ],
            tool_type="builtin",
        ),
        "handler": execute_knowledge_search,
    },
    "calculator": {
        "definition": ToolDefinition(
            name="calculator",
            description="Evaluates mathematical expressions safely",
            parameters=[
                ToolParameter(name="expression", type="string", description="Math expression, e.g., '2 + 2 * 4'")
            ],
            tool_type="builtin",
        ),
        "handler": execute_calculator,
    },
}
