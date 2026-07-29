import asyncio
import logging
from typing import Callable, Any
from .exceptions import PluginExecutionError

logger = logging.getLogger(__name__)

class PluginExecutor:
    def __init__(self, default_timeout: float = 5.0):
        self.default_timeout = default_timeout

    async def execute(self, plugin_id: str, func: Callable, *args, timeout: float = None, **kwargs) -> Any:
        timeout_val = timeout if timeout is not None else self.default_timeout
        try:
            # Enforce execution boundary and timeout
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_val)
        except asyncio.TimeoutError:
            logger.error(f"Plugin {plugin_id} timed out after {timeout_val}s")
            raise PluginExecutionError(f"Plugin {plugin_id} execution timed out")
        except Exception as e:
            logger.exception(f"Plugin {plugin_id} encountered an error: {str(e)}")
            raise PluginExecutionError(f"Plugin {plugin_id} execution failed: {str(e)}")
