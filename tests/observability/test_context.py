"""Tests for ObservabilityContext propagation."""

import pytest
from app.observability.context import (
    ObservabilityContext,
    get_current_context,
    set_current_context,
    clear_current_context,
    with_context,
)


def test_observability_context_creation():
    ctx = ObservabilityContext(
        tenant_id="tenant-123",
        workspace_id="ws-456",
        agent_id="agent-007",
    )
    assert ctx.tenant_id == "tenant-123"
    assert ctx.workspace_id == "ws-456"
    assert ctx.agent_id == "agent-007"
    assert ctx.trace_id is not None
    assert ctx.span_id is not None


def test_observability_context_dict_serialization():
    ctx = ObservabilityContext(
        execution_id="exec-99",
        model_id="gpt-4o",
        provider="openai",
    )
    d = ctx.to_dict()
    assert d["execution_id"] == "exec-99"
    assert d["model_id"] == "gpt-4o"
    assert d["provider"] == "openai"

    restored = ObservabilityContext.from_dict(d)
    assert restored.execution_id == "exec-99"
    assert restored.model_id == "gpt-4o"


def test_header_injection_and_extraction():
    ctx = ObservabilityContext(
        trace_id="tr-abc",
        span_id="sp-123",
        tenant_id="tenant-9",
    )
    headers = ctx.inject_headers()
    assert headers["x-trace-id"] == "tr-abc"
    assert headers["x-span-id"] == "sp-123"
    assert headers["x-tenant-id"] == "tenant-9"

    extracted = ObservabilityContext.extract_headers(headers)
    assert extracted.trace_id == "tr-abc"
    assert extracted.tenant_id == "tenant-9"


def test_with_context_manager():
    ctx = ObservabilityContext(execution_id="exec-scoped")
    with with_context(ctx):
        current = get_current_context()
        assert current.execution_id == "exec-scoped"

    # Context should be reset or default after context manager block
    clear_current_context()
    assert get_current_context().execution_id is None
