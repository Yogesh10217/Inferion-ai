"""Execution Timeline and Trace Graph representation."""

from __future__ import annotations

import time
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional


@dataclass
class ExecutionEvent:
    """Represents a discrete event or state change during execution."""
    name: str
    timestamp: float = field(default_factory=time.time)
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutionSpan:
    """Represents a node in the execution graph."""
    span_id: str
    trace_id: str
    name: str
    parent_span_id: Optional[str] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: float = 0.0
    status: str = "OK"
    component: str = "general"
    tokens: Dict[str, int] = field(default_factory=lambda: {"input": 0, "output": 0, "total": 0})
    cost: float = 0.0
    attributes: Dict[str, Any] = field(default_factory=dict)
    events: List[ExecutionEvent] = field(default_factory=list)
    children: List[ExecutionSpan] = field(default_factory=list)

    def calculate_duration(self) -> float:
        if self.end_time and self.start_time:
            self.duration_ms = round((self.end_time - self.start_time) * 1000.0, 2)
        return self.duration_ms

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "name": self.name,
            "parent_span_id": self.parent_span_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": self.duration_ms or self.calculate_duration(),
            "status": self.status,
            "component": self.component,
            "tokens": self.tokens,
            "cost": self.cost,
            "attributes": self.attributes,
            "events": [e.to_dict() if hasattr(e, "to_dict") else e for e in self.events],
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class ExecutionTimeline:
    """Flat chronological timeline representation of an execution tree."""
    trace_id: str
    execution_id: Optional[str]
    total_duration_ms: float
    total_cost: float
    total_tokens: int
    items: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ExecutionTrace:
    """Builds and serializes hierarchical trace trees and timelines from raw spans."""

    def __init__(self, trace_id: str, execution_id: Optional[str] = None) -> None:
        self.trace_id = trace_id
        self.execution_id = execution_id
        self.root_spans: List[ExecutionSpan] = []
        self._span_map: Dict[str, ExecutionSpan] = {}

    def add_raw_span(self, raw_span: Dict[str, Any]) -> ExecutionSpan:
        """Convert raw span dict into ExecutionSpan and place in tree."""
        span_id = raw_span.get("span_id", "")
        parent_id = raw_span.get("parent_span_id")
        name = raw_span.get("name", "unnamed")
        attrs = raw_span.get("attributes", {})
        
        component = attrs.get("component") or name.split(".")[0] if "." in name else "general"
        
        tokens = {
            "input": attrs.get("prompt_tokens", attrs.get("input_tokens", 0)),
            "output": attrs.get("completion_tokens", attrs.get("output_tokens", 0)),
            "total": attrs.get("total_tokens", 0),
        }
        if tokens["total"] == 0 and (tokens["input"] > 0 or tokens["output"] > 0):
            tokens["total"] = tokens["input"] + tokens["output"]

        cost = float(attrs.get("cost", 0.0))

        events = []
        for ev in raw_span.get("events", []):
            if isinstance(ev, dict):
                events.append(ExecutionEvent(name=ev.get("name", ""), timestamp=ev.get("timestamp", time.time()), attributes=ev.get("attributes", {})))
            elif isinstance(ev, ExecutionEvent):
                events.append(ev)

        exec_span = ExecutionSpan(
            span_id=span_id,
            trace_id=raw_span.get("trace_id", self.trace_id),
            name=name,
            parent_span_id=parent_id,
            start_time=raw_span.get("start_time", time.time()),
            end_time=raw_span.get("end_time"),
            duration_ms=raw_span.get("duration_ms", 0.0),
            status=raw_span.get("status", "OK"),
            component=component,
            tokens=tokens,
            cost=cost,
            attributes=attrs,
            events=events,
        )
        exec_span.calculate_duration()
        self._span_map[span_id] = exec_span
        return exec_span

    def build_tree(self, raw_spans: List[Dict[str, Any]]) -> List[ExecutionSpan]:
        """Build hierarchical execution graph from flat span list."""
        self._span_map.clear()
        self.root_spans.clear()

        for s in raw_spans:
            self.add_raw_span(s)

        for span in self._span_map.values():
            if span.parent_span_id and span.parent_span_id in self._span_map:
                parent = self._span_map[span.parent_span_id]
                if span not in parent.children:
                    parent.children.append(span)
            else:
                if span not in self.root_spans:
                    self.root_spans.append(span)

        # Sort children by start_time
        for span in self._span_map.values():
            span.children.sort(key=lambda c: c.start_time)

        self.root_spans.sort(key=lambda r: r.start_time)
        return self.root_spans

    def get_timeline(self) -> ExecutionTimeline:
        """Flatten execution graph into a chronological timeline with rollup metrics."""
        flat_items: List[Dict[str, Any]] = []
        total_cost = 0.0
        total_tokens = 0

        # Sort all spans in map by start_time
        sorted_spans = sorted(self._span_map.values(), key=lambda s: s.start_time)

        start_ref = sorted_spans[0].start_time if sorted_spans else time.time()
        end_ref = max([s.end_time or s.start_time for s in sorted_spans]) if sorted_spans else start_ref
        total_duration = round((end_ref - start_ref) * 1000.0, 2)

        for span in sorted_spans:
            total_cost += span.cost
            total_tokens += span.tokens.get("total", 0)
            offset_ms = round((span.start_time - start_ref) * 1000.0, 2)

            flat_items.append({
                "span_id": span.span_id,
                "parent_span_id": span.parent_span_id,
                "name": span.name,
                "component": span.component,
                "offset_ms": offset_ms,
                "duration_ms": span.duration_ms,
                "status": span.status,
                "cost": span.cost,
                "tokens": span.tokens,
                "events_count": len(span.events),
                "is_error": span.status.upper() in ["ERROR", "FAILED"],
            })

        return ExecutionTimeline(
            trace_id=self.trace_id,
            execution_id=self.execution_id,
            total_duration_ms=total_duration,
            total_cost=round(total_cost, 6),
            total_tokens=total_tokens,
            items=flat_items,
        )

    def find_failure_points(self) -> List[ExecutionSpan]:
        """Identify spans that failed or recorded errors."""
        failures = []
        for span in self._span_map.values():
            if span.status.upper() in ["ERROR", "FAILED"] or span.attributes.get("error"):
                failures.append(span)
        return failures

    def to_dict(self) -> Dict[str, Any]:
        """Serialize complete execution trace graph."""
        timeline = self.get_timeline()
        failures = [f.to_dict() for f in self.find_failure_points()]
        return {
            "trace_id": self.trace_id,
            "execution_id": self.execution_id,
            "total_duration_ms": timeline.total_duration_ms,
            "total_cost": timeline.total_cost,
            "total_tokens": timeline.total_tokens,
            "tree": [r.to_dict() for r in self.root_spans],
            "timeline": timeline.to_dict(),
            "failure_points": failures,
        }
