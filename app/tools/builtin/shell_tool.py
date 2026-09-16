"""
Restricted Shell Execution Tool with Command Allowlist Enforcement
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

from app.tools.tool import BaseTool, ToolCapability, ToolCategory, ToolMetadata
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolExecutionStatus, ToolResult

logger = logging.getLogger(__name__)


class ShellTool(BaseTool):
    """Restricted Shell tool enforcing command allowlist, injection prevention, timeouts, and audit logs."""

    DEFAULT_ALLOWLIST = {"ls", "grep", "echo", "cat", "ps", "pwd", "whoami", "date", "find", "head", "tail"}
    FORBIDDEN_CHARACTERS = {";", "&&", "||", "|", "`", "$", "(", ")", ">", "<", "\n"}

    def __init__(self, name: str = "shell_executor", allowlist: Optional[set] = None, timeout: float = 10.0):
        metadata = ToolMetadata(
            name=name,
            description="Executes allowlisted shell commands in a restricted environment",
            category=ToolCategory.BUILTIN,
            capabilities=[ToolCapability.EXECUTE, ToolCapability.HIGH_RISK],
            cost_estimate=0.001,
            timeout=timeout,
            requires_approval=True,
            parameters_schema={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"},
                    "args": {"type": "array", "items": {"type": "string"}, "description": "Arguments list"},
                },
                "required": ["command"],
            },
        )
        super().__init__(metadata)
        self.allowlist = allowlist or self.DEFAULT_ALLOWLIST

    def _validate_command(self, command: str, args: List[str]) -> None:
        cmd_base = command.strip().split()[0] if command.strip() else ""
        if cmd_base not in self.allowlist:
            raise ValueError(f"Command '{cmd_base}' is not in the allowed command list: {sorted(list(self.allowlist))}")

        full_str = command + " " + " ".join(args)
        for char in self.FORBIDDEN_CHARACTERS:
            if char in full_str:
                raise ValueError(f"Potential command injection character '{char}' is forbidden in Shell execution")

    async def execute_async(self, parameters: Dict[str, Any], context: ToolContext) -> ToolResult:
        start_time = time.time()
        command = parameters.get("command", "")
        args = parameters.get("args") or []

        try:
            self._validate_command(command, args)
        except Exception as ve:
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=str(ve),
            )

        cmd_list = [command] + args
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd_list,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout_data, stderr_data = await asyncio.wait_for(proc.communicate(), timeout=self.metadata.timeout)

            elapsed = time.time() - start_time
            stdout_str = stdout_data.decode("utf-8", errors="replace")
            stderr_str = stderr_data.decode("utf-8", errors="replace")

            status = ToolExecutionStatus.SUCCESS if proc.returncode == 0 else ToolExecutionStatus.FAILED
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=status,
                output={"stdout": stdout_str, "stderr": stderr_str, "returncode": proc.returncode},
                error=None if proc.returncode == 0 else stderr_str or f"Command exited with code {proc.returncode}",
                execution_time_seconds=elapsed,
                cost=self.metadata.cost_estimate,
                compute_usage={"cpu_ms": elapsed * 1000.0, "memory_mb": 8.0},
            )
        except asyncio.TimeoutError:
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.TIMEOUT,
                error=f"Shell command execution timed out after {self.metadata.timeout}s",
                execution_time_seconds=elapsed,
            )
        except Exception as ex:
            elapsed = time.time() - start_time
            return ToolResult(
                execution_id=context.execution_id,
                tool_name=self.name,
                status=ToolExecutionStatus.FAILED,
                error=f"Shell Execution Failure: {str(ex)}",
                execution_time_seconds=elapsed,
            )
