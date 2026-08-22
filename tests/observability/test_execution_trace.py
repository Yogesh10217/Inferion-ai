"""Tests for ExecutionTrace tree building and timeline generation."""

import time
import pytest
from app.observability.execution_trace import ExecutionTrace, ExecutionSpan


def test_execution_trace_tree_building():
    trace = ExecutionTrace(trace_id="tr-graph-1", execution_id="exec-g1")

    spans = [
        {
            "span_id": "root-1",
            "trace_id": "tr-graph-1",
            "name": "agent.execute",
            "parent_span_id": None,
            "start_time": 100.0,
            "end_time": 105.0,
            "duration_ms": 5000.0,
            "status": "OK",
            "attributes": {"execution_id": "exec-g1"},
        },
        {
            "span_id": "child-1",
            "trace_id": "tr-graph-1",
            "name": "tool.execute",
            "parent_span_id": "root-1",
            "start_time": 101.0,
            "end_time": 103.0,
            "duration_ms": 2000.0,
            "status": "OK",
            "attributes": {"execution_id": "exec-g1", "cost": 0.02, "prompt_tokens": 100, "completion_tokens": 50},
        },
    ]

    tree = trace.build_tree(spans)
    assert len(tree) == 1
    assert tree[0].span_id == "root-1"
    assert len(tree[0].children) == 1
    assert tree[0].children[0].span_id == "child-1"

    timeline = trace.get_timeline()
    assert timeline.total_duration_ms == 5000.0
    assert timeline.total_cost == 0.02
    assert timeline.total_tokens == 150
    assert len(timeline.items) == 2


def test_execution_trace_failures():
    trace = ExecutionTrace(trace_id="tr-fail-1")
    spans = [
        {"span_id": "s1", "name": "step1", "status": "ERROR", "start_time": 10.0, "end_time": 11.0},
        {"span_id": "s2", "name": "step2", "status": "OK", "start_time": 11.0, "end_time": 12.0},
    ]
    trace.build_tree(spans)
    failures = trace.find_failure_points()
    assert len(failures) == 1
    assert failures[0].span_id == "s1"
