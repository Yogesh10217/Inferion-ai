"""Distributed Tracing Manager integrating with OpenTelemetry context propagation."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from app.observability.context import ObservabilityContext, get_current_context, set_current_context
from app.observability.exceptions import SpanNotFoundException, TraceNotFoundException
from app.tracing.trace_context import SpanContext as OTelSpanContext
from app.tracing.tracer import Span as OTelSpan
from app.tracing.tracer import get_tracer

logger = logging.getLogger(__name__)


# Standard span names
SPAN_GATEWAY_REQUEST = "gateway.request"
SPAN_MODEL_INFERENCE = "model.inference"
SPAN_KNOWLEDGE_SEARCH = "knowledge.search"
SPAN_KNOWLEDGE_RETRIEVE = "knowledge.retrieve"
SPAN_AGENT_EXECUTE = "agent.execute"
SPAN_AGENT_REASON = "agent.reason"
SPAN_WORKFLOW_EXECUTE = "workflow.execute"
SPAN_WORKFLOW_NODE = "workflow.node"
SPAN_MEMORY_READ = "memory.read"
SPAN_MEMORY_WRITE = "memory.write"
SPAN_TOOL_VALIDATE = "tool.validate"
SPAN_TOOL_AUTHORIZE = "tool.authorize"
SPAN_TOOL_EXECUTE = "tool.execute"
SPAN_MCP_REQUEST = "mcp.request"
SPAN_TEAM_EXECUTE = "team.execute"
SPAN_TEAM_DELEGATE = "team.delegate"
SPAN_PLANNING_CREATE = "planning.create"
SPAN_PLANNING_SIMULATE = "planning.simulate"
SPAN_REASONING_EXECUTE = "reasoning.execute"
SPAN_AUTONOMY_EXECUTE = "autonomy.execute"
SPAN_WORKER_EXECUTE = "worker.execute"
SPAN_APPROVAL_REQUEST = "approval.request"
SPAN_APPROVAL_RESOLVE = "approval.resolve"


class TracingManager:
    """Manages creation, enrichment, retrieval, and lifecycle of distributed execution traces."""

    def __init__(self, tracer_name: str = "observability") -> None:
        self.tracer = get_tracer(tracer_name)
        # Store active spans by span_id in memory for fast lookup/graph construction
        self._active_spans: Dict[str, OTelSpan] = {}
        self._completed_spans: Dict[str, Dict[str, Any]] = {}
        self._traces: Dict[str, List[Dict[str, Any]]] = {}

    def start_trace(
        self,
        name: str = SPAN_GATEWAY_REQUEST,
        context: Optional[ObservabilityContext] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Initialize a top-level trace."""
        ctx = context or get_current_context()
        attrs = attributes or {}
        attrs.update(
            {
                "tenant_id": ctx.tenant_id,
                "organization_id": ctx.organization_id,
                "workspace_id": ctx.workspace_id,
                "execution_id": ctx.execution_id,
                "user_id": ctx.user_id,
            }
        )
        # Remove None values
        attrs = {k: v for k, v in attrs.items() if v is not None}

        otel_ctx = OTelSpanContext(trace_id=ctx.trace_id, span_id=ctx.span_id)
        span = self.tracer.start_span(name, parent_context=otel_ctx, attributes=attrs)
        self._active_spans[span.context.span_id] = span
        set_current_context(ctx)

        if ctx.trace_id not in self._traces:
            self._traces[ctx.trace_id] = []

        return span.to_dict()

    def end_trace(self, trace_id: str, status: str = "OK") -> Optional[Dict[str, Any]]:
        """Complete a trace by ending any remaining active root spans for the trace_id."""
        spans_to_end = [s for s in self._active_spans.values() if s.context.trace_id == trace_id]
        last_span_dict = None
        for span in spans_to_end:
            span.status = status
            span.end()
            span_dict = span.to_dict()
            self._completed_spans[span.context.span_id] = span_dict
            self._active_spans.pop(span.context.span_id, None)
            if span.context.trace_id in self._traces:
                self._traces[span.context.trace_id].append(span_dict)
            last_span_dict = span_dict
        return last_span_dict

    def start_span(
        self,
        name: str,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        context: Optional[ObservabilityContext] = None,
    ) -> OTelSpan:
        """Start a new span within the active context."""
        ctx = context or get_current_context()
        p_span_id = parent_span_id or ctx.span_id

        child_ctx = ctx.copy_with_span()
        attrs = attributes or {}
        attrs.update(
            {
                "tenant_id": child_ctx.tenant_id,
                "organization_id": child_ctx.organization_id,
                "workspace_id": child_ctx.workspace_id,
                "execution_id": child_ctx.execution_id,
                "agent_id": child_ctx.agent_id,
                "workflow_id": child_ctx.workflow_id,
                "worker_id": child_ctx.worker_id,
            }
        )
        attrs = {k: v for k, v in attrs.items() if v is not None}

        parent_otel_ctx = OTelSpanContext(trace_id=child_ctx.trace_id, span_id=p_span_id)
        span = self.tracer.start_span(name, parent_context=parent_otel_ctx, attributes=attrs)

        self._active_spans[span.context.span_id] = span
        set_current_context(child_ctx)
        return span

    def end_span(
        self,
        span: OTelSpan | str,
        status: str = "OK",
        attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """End a span and record its completed state."""
        span_id = span.context.span_id if isinstance(span, OTelSpan) else span
        active_span = self._active_spans.get(span_id)

        if not active_span and isinstance(span, OTelSpan):
            active_span = span

        if not active_span and isinstance(span, str):
            for s in reversed(list(self._active_spans.values())):
                if s.name == span:
                    active_span = s
                    span_id = s.context.span_id
                    break

        if not active_span:
            if span_id in self._completed_spans:
                return self._completed_spans[span_id]
            raise SpanNotFoundException(span_id)

        if attributes:
            active_span.set_attributes(attributes)
        active_span.status = status
        active_span.end()

        span_dict = active_span.to_dict()
        self._completed_spans[span_id] = span_dict
        self._active_spans.pop(span_id, None)

        trace_id = active_span.context.trace_id
        if trace_id not in self._traces:
            self._traces[trace_id] = []
        # Update or append
        self._traces[trace_id] = [s for s in self._traces[trace_id] if s["span_id"] != span_id]
        self._traces[trace_id].append(span_dict)

        return span_dict

    def record_exception(self, span: OTelSpan | str, exception: Exception) -> None:
        """Record an exception on a span."""
        span_obj = span if isinstance(span, OTelSpan) else self._active_spans.get(span)
        if span_obj:
            span_obj.record_exception(exception)

    def add_event(self, span: OTelSpan | str, name: str, attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add a event to a span."""
        span_obj = span if isinstance(span, OTelSpan) else self._active_spans.get(span)
        if span_obj:
            span_obj.add_event(name, attributes)

    def set_attribute(self, span: OTelSpan | str, key: str, value: Any) -> None:
        """Set a single attribute on a span."""
        span_obj = span if isinstance(span, OTelSpan) else self._active_spans.get(span)
        if span_obj:
            span_obj.set_attribute(key, value)

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """Retrieve all spans associated with a trace_id."""
        spans = self._traces.get(trace_id, [])
        # Also include any active spans for trace_id
        active = [s.to_dict() for s in self._active_spans.values() if s.context.trace_id == trace_id]
        combined = {s["span_id"]: s for s in spans + active}
        if not combined:
            raise TraceNotFoundException(trace_id)
        return list(combined.values())

    def get_execution_trace(self, execution_id: str) -> List[Dict[str, Any]]:
        """Retrieve all spans for a specific execution_id across traces."""
        matching_spans: List[Dict[str, Any]] = []
        for span_list in self._traces.values():
            for span in span_list:
                if span.get("attributes", {}).get("execution_id") == execution_id:
                    matching_spans.append(span)
        for span_obj in self._active_spans.values():
            s_dict = span_obj.to_dict()
            if s_dict.get("attributes", {}).get("execution_id") == execution_id:
                matching_spans.append(s_dict)
        return matching_spans
