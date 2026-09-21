"""Tests for FailureAnalyzer and root cause classification."""

from app.observability.failure_analysis import (
    BUDGET_EXCEEDED,
    MODEL_FAILURE,
    RATE_LIMIT,
    TIMEOUT,
    TOOL_FAILURE,
    FailureAnalyzer,
)


def test_failure_classification():
    fa = FailureAnalyzer()
    assert fa.identify_root_cause("HTTP 429 rate limit reached") == RATE_LIMIT
    assert fa.identify_root_cause("Operation timed out after 30s") == TIMEOUT
    assert fa.identify_root_cause("Tool schema validation failed", component="tool") == TOOL_FAILURE
    assert fa.identify_root_cause("Context window length exceeded", component="model") == MODEL_FAILURE
    assert fa.identify_root_cause("Insufficient funds in workspace budget") == BUDGET_EXCEEDED


def test_failure_analysis_report():
    fa = FailureAnalyzer()
    spans = [
        {"span_id": "sp-1", "name": "agent.execute", "status": "OK", "start_time": 1.0},
        {
            "span_id": "sp-2",
            "name": "tool.execute",
            "status": "ERROR",
            "status_description": "Connection timed out",
            "start_time": 2.0,
        },
    ]

    report = fa.analyze_failure("exec-f1", spans)
    assert report.primary_category == TIMEOUT
    assert report.root_cause_span_id == "sp-2"
    assert len(report.recommendations) >= 1
