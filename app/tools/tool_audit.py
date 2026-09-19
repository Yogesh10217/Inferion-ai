"""
Multi-tenant Audit Logging Subsystem for Enterprise Tool Calling
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult

logger = logging.getLogger("app.tools.audit")


class ToolAuditLogger:
    """Structured audit logger storing audit trails for tool execution and security events."""

    def __init__(self):
        self._audit_records: List[Dict[str, Any]] = []

    def _redact_secrets(self, data: Any) -> Any:
        """Redact sensitive keys like password, token, secret, api_key."""
        if isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                if any(
                    secret_kw in k.lower()
                    for secret_kw in ("password", "secret", "token", "api_key", "authorization", "bearer")
                ):
                    redacted[k] = "******"
                else:
                    redacted[k] = self._redact_secrets(v)
            return redacted
        elif isinstance(data, list):
            return [self._redact_secrets(i) for i in data]
        return data

    def log_execution_start(self, tool_name: str, parameters: Dict[str, Any], context: ToolContext) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "tool_execution_start",
            "execution_id": context.execution_id,
            "tool_name": tool_name,
            "tenant_id": context.tenant_id,
            "organization_id": context.organization_id,
            "workspace_id": context.workspace_id,
            "user_id": context.user_id,
            "user_role": context.user_role,
            "parameters": self._redact_secrets(parameters),
        }
        self._audit_records.append(record)
        logger.info(
            f"[AUDIT START] Tool '{tool_name}' (exec: {context.execution_id}, tenant: {context.tenant_id}, user: {context.user_id})"
        )

    def log_execution_completed(self, result: ToolResult, context: ToolContext) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "tool_execution_completed",
            "execution_id": context.execution_id,
            "tool_name": result.tool_name,
            "tenant_id": context.tenant_id,
            "organization_id": context.organization_id,
            "workspace_id": context.workspace_id,
            "user_id": context.user_id,
            "status": result.status.value,
            "execution_time_seconds": result.execution_time_seconds,
            "cost": result.cost,
            "error": result.error,
        }
        self._audit_records.append(record)
        logger.info(
            f"[AUDIT END] Tool '{result.tool_name}' status={result.status.value} duration={result.execution_time_seconds:.3f}s cost=${result.cost:.4f}"
        )

    def log_security_block(self, tool_name: str, context: ToolContext, reason: str) -> None:
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event_type": "security_block",
            "execution_id": context.execution_id,
            "tool_name": tool_name,
            "tenant_id": context.tenant_id,
            "user_id": context.user_id,
            "reason": reason,
        }
        self._audit_records.append(record)
        logger.warning(f"[AUDIT BLOCK] Tool '{tool_name}' blocked for user '{context.user_id}': {reason}")

    def get_audit_logs(
        self,
        tenant_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        logs = self._audit_records
        if tenant_id:
            logs = [log for log in logs if log.get("tenant_id") == tenant_id]
        if tool_name:
            logs = [log for log in logs if log.get("tool_name") == tool_name]
        return logs[-limit:]
