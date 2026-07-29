import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class RoutingContext:
    """Carries execution context, request metadata, and decision explanation traces."""

    request_metadata: Dict[str, Any] = field(default_factory=dict)
    shadow_routing: bool = False
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    required_capabilities: List[str] = field(default_factory=list)
    decision_explanation: Dict[str, Any] = field(default_factory=dict)
    _traces: List[Dict[str, Any]] = field(default_factory=list)

    def record_trace(self, stage: str, data: Any):
        """Record step-by-step decision trace."""
        trace_entry = {
            "stage": stage,
            "timestamp": time.time(),
            "data": data,
        }
        self._traces.append(trace_entry)
        self.decision_explanation[stage] = data

    def get_full_trace(self) -> List[Dict[str, Any]]:
        return list(self._traces)
