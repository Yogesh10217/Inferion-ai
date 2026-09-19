"""
Tool Factory for Dynamic Tool Creation
"""

import inspect
from typing import Any, Callable, Dict, Optional

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult


class GenericFunctionTool(BaseTool):
    """Wraps a standard Python function into a Platform BaseTool."""

    def __init__(self, func: Callable, metadata: ToolMetadata):
        super().__init__(metadata)
        self.func = func

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        import time

        start_time = time.time()
        try:
            if inspect.iscoroutinefunction(self.func):
                output = await self.func(**parameters)
            else:
                output = self.func(**parameters)

            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.SUCCESS,
                output=output,
                execution_time_seconds=elapsed,
                cost=self.metadata.cost_estimate,
            )
        except Exception as e:
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=str(e),
                execution_time_seconds=elapsed,
            )


class ToolFactory:
    """Factory for instantiating tools from callables, dicts, or schemas."""

    @staticmethod
    def from_function(
        func: Callable,
        name: Optional[str] = None,
        description: Optional[str] = None,
        category: ToolCategory = ToolCategory.CUSTOM,
        capabilities: Optional[list] = None,
        cost_estimate: float = 0.0,
        requires_approval: bool = False,
    ) -> BaseTool:
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or f"Function {tool_name}"

        # Generate JSON schema from signature parameters
        sig = inspect.signature(func)
        properties = {}
        required = []
        for p_name, param in sig.parameters.items():
            if p_name in ("context", "self"):
                continue
            properties[p_name] = {"type": "string", "description": f"Parameter {p_name}"}
            if param.default == inspect.Parameter.empty:
                required.append(p_name)

        params_schema = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        metadata = ToolMetadata(
            name=tool_name,
            description=tool_desc,
            category=category,
            capabilities=capabilities or [ToolCapability.READ],
            cost_estimate=cost_estimate,
            parameters_schema=params_schema,
            requires_approval=requires_approval,
        )

        return GenericFunctionTool(func, metadata)
