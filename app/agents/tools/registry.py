"""
Dynamic Tool Registry
"""

import logging
from typing import Any, Awaitable, Callable, Dict

from app.agents.exceptions import ToolNotFoundError
from app.agents.tools.builtin import BUILTIN_TOOLS
from app.agents.tools.python import execute_python_code
from app.agents.tools.schemas import ToolDefinition, ToolParameter
from app.agents.tools.shell import execute_shell_command

logger = logging.getLogger(__name__)

ToolHandler = Callable[..., Awaitable[Dict[str, Any]]]


class ToolRegistry:
    def __init__(self):
        self._definitions: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, ToolHandler] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        # Builtin tools
        for name, item in BUILTIN_TOOLS.items():
            self.register_tool(item["definition"], item["handler"])

        # Python interpreter tool
        self.register_tool(
            ToolDefinition(
                name="python_interpreter",
                description="Runs Python code in an isolated environment",
                parameters=[ToolParameter(name="code", type="string", description="Python code to execute")],
                required_scopes=["developer"],
                tool_type="python"
            ),
            execute_python_code
        )

        # Shell command tool
        self.register_tool(
            ToolDefinition(
                name="shell_executor",
                description="Executes shell commands asynchronously",
                parameters=[ToolParameter(name="command", type="string", description="Shell command string")],
                required_scopes=["admin"],
                tool_type="shell"
            ),
            execute_shell_command
        )

    def register_tool(self, definition: ToolDefinition, handler: ToolHandler) -> None:
        self._definitions[definition.name] = definition
        self._handlers[definition.name] = handler
        logger.info(f"Registered tool '{definition.name}' ({definition.tool_type})")

    def get_definition(self, name: str) -> ToolDefinition:
        def_obj = self._definitions.get(name)
        if not def_obj:
            raise ToolNotFoundError(f"Tool '{name}' not found in registry")
        return def_obj

    def get_handler(self, name: str) -> ToolHandler:
        handler = self._handlers.get(name)
        if not handler:
            raise ToolNotFoundError(f"Tool '{name}' handler not found")
        return handler

    def list_tools(self) -> Dict[str, ToolDefinition]:
        return dict(self._definitions)
