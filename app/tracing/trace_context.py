import secrets
from dataclasses import dataclass, field
from typing import Dict, Optional


def generate_trace_id() -> str:
    """Generate 128-bit trace ID formatted as 32 hex characters."""
    return secrets.token_hex(16)


def generate_span_id() -> str:
    """Generate 64-bit span ID formatted as 16 hex characters."""
    return secrets.token_hex(8)


@dataclass
class SpanContext:
    trace_id: str = field(default_factory=generate_trace_id)
    span_id: str = field(default_factory=generate_span_id)
    trace_flags: str = "01"  # 01 = sampled
    tracestate: str = ""
    baggage: Dict[str, str] = field(default_factory=dict)
    is_remote: bool = False

    def to_traceparent(self) -> str:
        """Format as W3C traceparent string: 00-{trace_id}-{span_id}-{trace_flags}"""
        return f"00-{self.trace_id}-{self.span_id}-{self.trace_flags}"

    @classmethod
    def from_traceparent(cls, traceparent: str, baggage: Optional[Dict[str, str]] = None) -> Optional["SpanContext"]:
        """Parse W3C traceparent header string."""
        if not traceparent or not isinstance(traceparent, str):
            return None
        parts = traceparent.strip().split("-")
        if len(parts) != 4 or parts[0] != "00":
            return None
        return cls(
            trace_id=parts[1],
            span_id=parts[2],
            trace_flags=parts[3],
            baggage=baggage or {},
            is_remote=True,
        )
