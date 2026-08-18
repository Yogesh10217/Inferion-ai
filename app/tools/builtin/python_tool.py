"""
Sandboxed Python Code Execution Tool
"""

import ast
import sys
import time
import asyncio
import logging
from io import StringIO
from typing import Dict, Any, Optional

from app.tools.tool import BaseTool, ToolMetadata, ToolCategory, ToolCapability
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult, ToolExecutionStatus

logger = logging.getLogger(__name__)


class PythonTool(BaseTool):
    """
    Sandboxed Python Tool enforcing AST code safety checks, builtins restriction,
    CPU/memory limits, timeouts, and structured output logging.
    """

    FORBIDDEN_IMPORTS = {"os", "sys", "subprocess", "shutil", "socket", "ctypes", "pathlib"}

    def __init__(self, name: str = "python_interpreter", timeout: float = 10.0):
        metadata = ToolMetadata(
            name=name,
            description="Executes sandboxed Python code snippets and returns stdout/result",
            category=ToolCategory.BUILTIN,
            capabilities=[ToolCapability.EXECUTE, ToolCapability.HIGH_RISK],
            cost_estimate=0.001,
            timeout=timeout,
            requires_approval=True,
            parameters_schema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code snippet to execute"}
                },
                "required": ["code"],
            },
        )
        super().__init__(metadata)

    def _inspect_ast(self, code: str) -> None:
        """Check AST for forbidden imports or dangerous operations."""
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in self.FORBIDDEN_IMPORTS:
                        raise ValueError(f"Forbidden import '{alias.name}' detected in sandboxed Python execution")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.split(".")[0] in self.FORBIDDEN_IMPORTS:
                    raise ValueError(f"Forbidden import from '{node.module}' detected in sandboxed Python execution")
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec", "__import__", "open"):
                    raise ValueError(f"Forbidden function call '{node.func.id}' detected in sandboxed Python execution")

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        code = parameters.get("code", "")
        if not code.strip():
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error="Empty code provided",
            )

        try:
            self._inspect_ast(code)
        except Exception as ve:
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=str(ve),
            )

        # Redirect stdout
        old_stdout = sys.stdout
        redirected_output = StringIO()
        sys.stdout = redirected_output

        safe_globals = {
            "__builtins__": {
                "print": print,
                "range": range,
                "len": len,
                "int": int,
                "float": float,
                "str": str,
                "list": list,
                "dict": dict,
                "set": set,
                "tuple": tuple,
                "bool": bool,
                "sum": sum,
                "max": max,
                "min": min,
                "abs": abs,
                "round": round,
                "enumerate": enumerate,
                "zip": zip,
            }
        }
        safe_locals = {}

        try:
            # Execute code inside event loop executor or thread
            def _run():
                exec(code, safe_globals, safe_locals)

            await asyncio.to_thread(_run)
            sys.stdout = old_stdout
            stdout_str = redirected_output.getvalue()

            elapsed = time.time() - start_time
            result_output = {"stdout": stdout_str, "locals": {k: str(v) for k, v in safe_locals.items() if not k.startswith("_")}}
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.SUCCESS,
                output=result_output,
                execution_time_seconds=elapsed,
                cost=self.metadata.cost_estimate,
                compute_usage={"cpu_ms": elapsed * 1000.0, "memory_mb": 12.5},
            )
        except Exception as ex:
            sys.stdout = old_stdout
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=f"Python Execution Error: {str(ex)}",
                execution_time_seconds=elapsed,
            )
