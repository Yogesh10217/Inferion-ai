"""
Python Code Interpreter Tool
"""

import sys
import io
import logging
from typing import Dict, Any
from app.agents.agent_context import AgentContext

logger = logging.getLogger(__name__)


async def execute_python_code(code: str, context: AgentContext) -> Dict[str, Any]:
    """
    Executes Python code snippet in isolated namespace and captures stdout/stderr.
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    
    local_scope: Dict[str, Any] = {}
    error_msg = None
    
    try:
        exec(code, {"__builtins__": __builtins__}, local_scope)
    except Exception as e:
        error_msg = str(e)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    stdout_val = redirected_output.getvalue()
    stderr_val = redirected_error.getvalue()
    
    return {
        "stdout": stdout_val,
        "stderr": stderr_val,
        "result": local_scope.get("result"),
        "error": error_msg,
        "success": error_msg is None
    }
