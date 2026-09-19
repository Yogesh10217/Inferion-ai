"""Unified Observability Context propagation across platform layers."""

from __future__ import annotations

import contextvars
import uuid
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Generator, Optional


@dataclass
class ObservabilityContext:
    """Unified context holding correlation and execution parameters across all platform layers.

    Propagates across Request -> Agent -> Workflow -> Tool -> MCP -> Multi-Agent Team -> Planning -> Autonomous Execution.
    """

    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: Optional[str] = None
    request_id: Optional[str] = None
    execution_id: Optional[str] = None
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    team_id: Optional[str] = None
    worker_id: Optional[str] = None
    tool_execution_id: Optional[str] = None
    tenant_id: Optional[str] = None
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    model_id: Optional[str] = None
    provider: Optional[str] = None
    correlation_id: Optional[str] = None
    baggage: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize context to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ObservabilityContext:
        """Create an ObservabilityContext from a dictionary."""
        valid_keys = {
            "trace_id",
            "span_id",
            "parent_span_id",
            "request_id",
            "execution_id",
            "workflow_id",
            "agent_id",
            "team_id",
            "worker_id",
            "tool_execution_id",
            "tenant_id",
            "organization_id",
            "workspace_id",
            "user_id",
            "model_id",
            "provider",
            "correlation_id",
            "baggage",
        }
        filtered = {k: v for k, v in data.items() if k in valid_keys}
        if "baggage" in filtered and not isinstance(filtered["baggage"], dict):
            filtered["baggage"] = {}
        return cls(**filtered)

    def inject_headers(self, headers: Dict[str, str] | None = None) -> Dict[str, str]:
        """Inject context into HTTP or RPC headers."""
        headers = headers if headers is not None else {}
        headers["x-trace-id"] = self.trace_id
        headers["x-span-id"] = self.span_id
        if self.parent_span_id:
            headers["x-parent-span-id"] = self.parent_span_id
        if self.request_id:
            headers["x-request-id"] = self.request_id
        if self.execution_id:
            headers["x-execution-id"] = self.execution_id
        if self.tenant_id:
            headers["x-tenant-id"] = self.tenant_id
        if self.organization_id:
            headers["x-org-id"] = self.organization_id
        if self.workspace_id:
            headers["x-workspace-id"] = self.workspace_id
        if self.correlation_id:
            headers["x-correlation-id"] = self.correlation_id
        return headers

    @classmethod
    def extract_headers(cls, headers: Dict[str, str]) -> ObservabilityContext:
        """Extract context from HTTP or RPC headers."""
        norm = {k.lower(): v for k, v in headers.items()}
        trace_id = norm.get("x-trace-id")
        if not trace_id and norm.get("traceparent"):
            parts = norm["traceparent"].split("-")
            if len(parts) >= 2:
                trace_id = parts[1]
        if not trace_id:
            trace_id = uuid.uuid4().hex

        span_id = norm.get("x-span-id") or uuid.uuid4().hex[:16]
        return cls(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=norm.get("x-parent-span-id"),
            request_id=norm.get("x-request-id"),
            execution_id=norm.get("x-execution-id"),
            tenant_id=norm.get("x-tenant-id"),
            organization_id=norm.get("x-org-id") or norm.get("x-organization-id"),
            workspace_id=norm.get("x-workspace-id"),
            correlation_id=norm.get("x-correlation-id"),
        )

    def copy_with_span(self, new_span_id: Optional[str] = None) -> ObservabilityContext:
        """Create a child context preserving trace context."""
        child = ObservabilityContext.from_dict(self.to_dict())
        child.parent_span_id = self.span_id
        child.span_id = new_span_id or uuid.uuid4().hex[:16]
        return child


# Global contextvar holding active context
_observability_context_var: contextvars.ContextVar[Optional[ObservabilityContext]] = contextvars.ContextVar(
    "_observability_context_var", default=None
)


def get_current_context() -> ObservabilityContext:
    """Retrieve the current active ObservabilityContext or create a default one."""
    ctx = _observability_context_var.get()
    if ctx is None:
        ctx = ObservabilityContext()
        _observability_context_var.set(ctx)
    return ctx


def set_current_context(ctx: ObservabilityContext) -> contextvars.Token:
    """Set current ObservabilityContext."""
    return _observability_context_var.set(ctx)


def clear_current_context(token: Optional[contextvars.Token] = None) -> None:
    """Clear or reset ObservabilityContext."""
    if token:
        _observability_context_var.reset(token)
    else:
        _observability_context_var.set(None)


@contextmanager
def with_context(ctx: ObservabilityContext) -> Generator[ObservabilityContext, None, None]:
    """Context manager for scoping an ObservabilityContext."""
    token = set_current_context(ctx)
    try:
        yield ctx
    finally:
        clear_current_context(token)
