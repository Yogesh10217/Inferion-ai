"""
Tool Parameter and Input Validator
"""

import logging
from typing import Dict, Any, List
from app.tools.tool import BaseTool, ToolMetadata
from app.tools.exceptions import ToolValidationError

logger = logging.getLogger(__name__)


class ToolValidator:
    """Validates execution inputs against schema declarations."""

    @staticmethod
    def validate_parameters(tool: BaseTool, parameters: Dict[str, Any]) -> bool:
        """Validate parameters dictionary against tool's parameters_schema."""
        schema = tool.metadata.parameters_schema
        if not schema or not isinstance(schema, dict):
            return True

        req_fields = schema.get("required", [])
        for field in req_fields:
            if field not in parameters:
                raise ToolValidationError(f"Missing required parameter '{field}' for tool '{tool.name}'")

        # Type checks if properties specified
        props = schema.get("properties", {})
        for key, val in parameters.items():
            if key in props:
                expected_type = props[key].get("type")
                if expected_type == "string" and not isinstance(val, str):
                    raise ToolValidationError(f"Parameter '{key}' must be a string (got {type(val).__name__})")
                elif expected_type == "integer" and not isinstance(val, int):
                    raise ToolValidationError(f"Parameter '{key}' must be an integer (got {type(val).__name__})")
                elif expected_type == "number" and not isinstance(val, (int, float)):
                    raise ToolValidationError(f"Parameter '{key}' must be a number (got {type(val).__name__})")
                elif expected_type == "boolean" and not isinstance(val, bool):
                    raise ToolValidationError(f"Parameter '{key}' must be a boolean (got {type(val).__name__})")
                elif expected_type == "array" and not isinstance(val, list):
                    raise ToolValidationError(f"Parameter '{key}' must be an array (got {type(val).__name__})")
                elif expected_type == "object" and not isinstance(val, dict):
                    raise ToolValidationError(f"Parameter '{key}' must be an object (got {type(val).__name__})")

        return True
