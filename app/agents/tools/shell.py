"""
Shell Command Execution Tool
"""

import asyncio
import logging
from typing import Any, Dict

from app.agents.agent_context import AgentContext

logger = logging.getLogger(__name__)


async def execute_shell_command(command: str, context: AgentContext, timeout_seconds: float = 10.0) -> Dict[str, Any]:
    """
    Executes shell command asynchronously with timeout safeguard.
    """
    try:
        proc = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout_data, stderr_data = await asyncio.wait_for(
            proc.communicate(), timeout=timeout_seconds
        )
        return {
            "command": command,
            "stdout": stdout_data.decode("utf-8", errors="replace"),
            "stderr": stderr_data.decode("utf-8", errors="replace"),
            "exit_code": proc.returncode,
            "success": proc.returncode == 0
        }
    except asyncio.TimeoutError:
        return {
            "command": command,
            "stdout": "",
            "stderr": f"Execution timed out after {timeout_seconds} seconds",
            "exit_code": -1,
            "success": False
        }
    except Exception as e:
        return {
            "command": command,
            "stdout": "",
            "stderr": str(e),
            "exit_code": -1,
            "success": False
        }
