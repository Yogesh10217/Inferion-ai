"""
Core Execution Engine for Enterprise Tool Calling & MCP Platform
"""

import time
import asyncio
import logging
from typing import Dict, Any, List, Optional, AsyncGenerator

from app.tools.tool import RetryPolicy
from app.tools.tool_context import ToolContext
from app.tools.tool_result import ToolResult, ToolExecutionStatus
from app.tools.tool_registry import ToolRegistry
from app.tools.tool_validator import ToolValidator
from app.tools.tool_permissions import ToolPermissionEngine
from app.tools.tool_audit import ToolAuditLogger
from app.tools.tool_billing import ToolBillingTracker
from app.tools.exceptions import (
    ToolTimeoutException,
    ToolApprovalRequiredException,
)
from app.tools.tool_metrics import (
    tool_calls_total,
    tool_failures_total,
    tool_duration_seconds,
    tool_cost_total,
    tool_active_executions,
)

# OpenTelemetry optional import fallback
try:
    from opentelemetry import trace
    tracer = trace.get_tracer("app.tools.executor")
except ImportError:
    class DummySpan:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def set_attribute(self, key, value):
            pass

        def set_status(self, status, description=None):
            pass

        def record_exception(self, exception):
            pass

    class DummyTracer:
        def start_as_current_span(self, name, **kwargs):
            return DummySpan()

    tracer = DummyTracer()

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes tools with timeouts, retries, OpenTelemetry spans, audit logging, and billing."""

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        permission_engine: Optional[ToolPermissionEngine] = None,
        audit_logger: Optional[ToolAuditLogger] = None,
        billing_tracker: Optional[ToolBillingTracker] = None,
    ):
        self.registry = registry or ToolRegistry()
        self.permission_engine = permission_engine or ToolPermissionEngine()
        self.audit_logger = audit_logger or ToolAuditLogger()
        self.billing_tracker = billing_tracker or ToolBillingTracker()

    async def execute_async(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[ToolContext] = None,
        tenant_id: Optional[str] = None,
        version: Optional[str] = None,
    ) -> ToolResult:
        ctx = context or ToolContext(tenant_id=tenant_id or "default_tenant")
        tid = ctx.tenant_id

        # 1. OpenTelemetry span for validation
        with tracer.start_as_current_span("tool.validate") as span:
            span.set_attribute("tool.name", tool_name)
            span.set_attribute("tenant.id", tid)
            try:
                tool = self.registry.get_tool(tool_name, tenant_id=tid, version=version)
                ToolValidator.validate_parameters(tool, parameters)
            except Exception as ve:
                self.audit_logger.log_security_block(tool_name, ctx, str(ve))
                tool_failures_total.labels(tool_name=tool_name, error_type=type(ve).__name__, tenant_id=tid).inc()
                raise ve

        # 2. OpenTelemetry span for authorization
        with tracer.start_as_current_span("tool.authorize") as span:
            span.set_attribute("tool.name", tool_name)
            try:
                self.permission_engine.validate_execution(tool, ctx, cost_estimate=tool.metadata.cost_estimate)
            except ToolApprovalRequiredException as e:
                self.audit_logger.log_security_block(tool_name, ctx, f"Approval Required: {str(e)}")
                return ToolResult(
                    execution_id=ctx.execution_id,
                    tool_name=tool_name,
                    status=ToolExecutionStatus.PENDING_APPROVAL,
                    error=str(e),
                )
            except Exception as pe:
                self.audit_logger.log_security_block(tool_name, ctx, str(pe))
                tool_failures_total.labels(tool_name=tool_name, error_type=type(pe).__name__, tenant_id=tid).inc()
                raise pe

        # Audit start log
        self.audit_logger.log_execution_start(tool_name, parameters, ctx)
        tool_active_executions.labels(tool_name=tool_name).inc()

        start_time = time.time()
        retry_policy = tool.metadata.retry_policy or RetryPolicy()
        max_attempts = max(1, retry_policy.max_retries + 1)
        delay = retry_policy.initial_delay_seconds

        last_exception = None
        result: Optional[ToolResult] = None

        try:
            with tracer.start_as_current_span("tool.execute") as span:
                span.set_attribute("tool.name", tool_name)
                for attempt in range(1, max_attempts + 1):
                    try:
                        # Enforce timeout via asyncio.wait_for
                        timeout_sec = tool.metadata.timeout
                        coro = tool.execute_async(parameters, ctx)
                        result = await asyncio.wait_for(coro, timeout=timeout_sec)
                        if result.is_success():
                            break
                        # Retry if status is failed
                        if attempt < max_attempts:
                            await asyncio.sleep(delay)
                            delay *= retry_policy.backoff_factor
                    except asyncio.TimeoutError:
                        last_exception = ToolTimeoutException(f"Tool '{tool_name}' timed out after {tool.metadata.timeout}s")
                        if attempt < max_attempts:
                            await asyncio.sleep(delay)
                            delay *= retry_policy.backoff_factor
                    except asyncio.CancelledError:
                        elapsed = time.time() - start_time
                        res = ToolResult(
                            execution_id=ctx.execution_id,
                            tool_name=tool_name,
                            status=ToolExecutionStatus.CANCELLED,
                            error="Tool execution cancelled by caller",
                            execution_time_seconds=elapsed,
                        )
                        self._record_telemetry(res, ctx)
                        return res
                    except Exception as ex:
                        last_exception = ex
                        if attempt < max_attempts:
                            await asyncio.sleep(delay)
                            delay *= retry_policy.backoff_factor

                elapsed = time.time() - start_time
                if not result or not result.is_success():
                    error_msg = str(last_exception) if last_exception else (result.error if result else "Execution failed")
                    status_val = ToolExecutionStatus.TIMEOUT if isinstance(last_exception, ToolTimeoutException) else ToolExecutionStatus.FAILED
                    result = ToolResult(
                        execution_id=ctx.execution_id,
                        tool_name=tool_name,
                        status=status_val,
                        error=error_msg,
                        execution_time_seconds=elapsed,
                    )
        finally:
            tool_active_executions.labels(tool_name=tool_name).dec()

        # Telemetry, Audit, Billing
        self._record_telemetry(result, ctx)
        return result

    def execute(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[ToolContext] = None,
        tenant_id: Optional[str] = None,
    ) -> ToolResult:
        """Synchronous execution wrapper."""
        return asyncio.run(self.execute_async(tool_name, parameters, context, tenant_id))

    async def execute_batch(
        self,
        requests: List[Dict[str, Any]],
        context: Optional[ToolContext] = None,
    ) -> List[ToolResult]:
        """Execute a batch of tool requests concurrently."""
        tasks = [
            self.execute_async(
                tool_name=req["tool_name"],
                parameters=req.get("parameters", {}),
                context=context,
                tenant_id=req.get("tenant_id"),
                version=req.get("version"),
            )
            for req in requests
        ]
        return await asyncio.gather(*tasks, return_exceptions=False)

    async def execute_stream(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
        context: Optional[ToolContext] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream execution updates and final result."""
        yield {"event": "start", "tool_name": tool_name, "status": "running"}
        res = await self.execute_async(tool_name, parameters, context)
        yield {"event": "completed", "result": res.to_dict()}

    def _record_telemetry(self, result: ToolResult, context: ToolContext) -> None:
        tid = context.tenant_id
        tname = result.tool_name

        # OTEL spans for complete / failed
        span_name = "tool.complete" if result.is_success() else "tool.failed"
        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("tool.name", tname)
            span.set_attribute("tool.status", result.status.value)
            span.set_attribute("tool.execution_time", result.execution_time_seconds)

        # Prometheus metrics
        tool_calls_total.labels(tool_name=tname, status=result.status.value, tenant_id=tid).inc()
        tool_duration_seconds.labels(tool_name=tname, tenant_id=tid).observe(result.execution_time_seconds)
        if result.cost > 0:
            tool_cost_total.labels(tool_name=tname, tenant_id=tid).inc(result.cost)

        if not result.is_success():
            tool_failures_total.labels(tool_name=tname, error_type=result.status.value, tenant_id=tid).inc()

        # Audit & Billing
        self.audit_logger.log_execution_completed(result, context)
        self.billing_tracker.track_execution(result, context)
