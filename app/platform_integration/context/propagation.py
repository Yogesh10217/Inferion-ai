"""Trace and Context Propagation Engine for Phase 5.58."""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.platform_integration.models import TraceContext

logger = logging.getLogger(__name__)


class ContextPropagationEngine:
    """Manages metadata and trace context propagation across cross-phase operations."""

    @staticmethod
    def spawn_child_context(
        parent: TraceContext,
        target_platform: str,
        causation_id: Optional[str] = None,
        parent_event_id: Optional[str] = None,
    ) -> TraceContext:
        """Spawns a child TraceContext retaining trace_id and correlation_id."""
        return TraceContext(
            trace_id=parent.trace_id,
            correlation_id=parent.correlation_id,
            causation_id=causation_id or parent.causation_id,
            parent_event_id=parent_event_id or parent.parent_event_id,
            tenant_id=parent.tenant_id,
            source_platform=target_platform,
            timestamp=datetime.now(timezone.utc),
        )

    @staticmethod
    def inject_trace_headers(context: TraceContext) -> Dict[str, str]:
        """Injects trace identifiers into outbound metadata headers."""
        return {
            "X-Trace-ID": context.trace_id,
            "X-Correlation-ID": context.correlation_id,
            "X-Tenant-ID": context.tenant_id,
            "X-Source-Platform": context.source_platform,
        }

    @staticmethod
    def extract_trace_context(headers: Dict[str, str], default_tenant: str = "default") -> TraceContext:
        """Extracts trace identifiers from inbound metadata headers."""
        return TraceContext(
            trace_id=headers.get("X-Trace-ID", headers.get("x-trace-id", "")),
            correlation_id=headers.get("X-Correlation-ID", headers.get("x-correlation-id", "")),
            tenant_id=headers.get("X-Tenant-ID", headers.get("x-tenant-id", default_tenant)),
            source_platform=headers.get("X-Source-Platform", headers.get("x-source-platform", "UNKNOWN")),
        )
