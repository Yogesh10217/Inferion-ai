"""
Secure Tool Executor Engine
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional
from app.agents.tools.registry import ToolRegistry
from app.agents.tools.permissions import ToolPermissionChecker
from app.agents.agent_context import AgentContext
from app.agents.cache import AgentCache
from app.agents.budget import AgentBudgetTracker
from app.agents.exceptions import ToolExecutionError

logger = logging.getLogger(__name__)


class ToolExecutor:
    def __init__(self, registry: Optional[ToolRegistry] = None, cache: Optional[AgentCache] = None):
        self.registry = registry or ToolRegistry()
        self.cache = cache or AgentCache()

    async def execute_tool(
        self,
        tool_name: str,
        kwargs: Dict[str, Any],
        context: AgentContext,
        budget_tracker: Optional[AgentBudgetTracker] = None
    ) -> Dict[str, Any]:
        definition = self.registry.get_definition(tool_name)
        handler = self.registry.get_handler(tool_name)

        # 1. RBAC / Permission Scope Validation
        ToolPermissionChecker.check_permissions(tool_name, definition.required_scopes, context)

        # 2. Check Tool Result Cache
        cache_key = {"tool_name": tool_name, "args": kwargs, "org": context.organization_id}
        cached_res = self.cache.get("tool_execution", cache_key)
        if cached_res is not None:
            logger.info(f"Tool '{tool_name}' result fetched from cache")
            return cached_res

        # 3. Execution with Timeout & Retry
        start_time = time.time()
        attempt = 0
        last_error = None

        while attempt <= definition.max_retries:
            try:
                attempt += 1
                result = await asyncio.wait_for(
                    handler(**kwargs, context=context),
                    timeout=definition.timeout_seconds
                )
                duration = time.time() - start_time

                # Track estimated cost if budget tracker provided
                if budget_tracker and definition.cost_estimate_dollars > 0:
                    budget_tracker.add_usage(0, 0, estimated_cost=definition.cost_estimate_dollars)

                execution_output = {
                    "tool_name": tool_name,
                    "status": "SUCCESS",
                    "result": result,
                    "duration_seconds": duration,
                    "attempts": attempt
                }

                # Store in cache
                self.cache.set("tool_execution", cache_key, execution_output)
                return execution_output

            except asyncio.TimeoutError:
                last_error = f"Tool execution timed out after {definition.timeout_seconds}s"
                logger.warning(f"Tool '{tool_name}' attempt {attempt} failed: {last_error}")
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Tool '{tool_name}' attempt {attempt} failed: {last_error}")

        raise ToolExecutionError(f"Tool '{tool_name}' failed after {attempt} attempts. Last error: {last_error}")
