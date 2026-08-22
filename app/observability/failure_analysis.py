"""AI Root Cause Failure Analysis Subsystem."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Standard Failure Categories
MODEL_FAILURE = "MODEL_FAILURE"
PROVIDER_FAILURE = "PROVIDER_FAILURE"
TOOL_FAILURE = "TOOL_FAILURE"
MCP_FAILURE = "MCP_FAILURE"
WORKFLOW_FAILURE = "WORKFLOW_FAILURE"
AGENT_FAILURE = "AGENT_FAILURE"
MEMORY_FAILURE = "MEMORY_FAILURE"
KNOWLEDGE_FAILURE = "KNOWLEDGE_FAILURE"
TIMEOUT = "TIMEOUT"
RATE_LIMIT = "RATE_LIMIT"
AUTHORIZATION_FAILURE = "AUTHORIZATION_FAILURE"
BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
APPROVAL_REJECTED = "APPROVAL_REJECTED"
SYSTEM_FAILURE = "SYSTEM_FAILURE"


@dataclass
class FailureReport:
    """Comprehensive diagnostic report summarizing execution failure root cause."""
    execution_id: str
    trace_id: str
    primary_category: str
    root_cause_span_id: Optional[str]
    root_cause_message: str
    failure_chain: List[Dict[str, Any]]
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FailureAnalyzer:
    """Analyzes trace spans and error outputs to pinpoint root cause failure chains."""

    def __init__(self) -> None:
        pass

    def identify_root_cause(self, error_message: str, component: str = "general") -> str:
        """Classify failure type based on error payload inspection."""
        msg_lower = error_message.lower()

        if "timeout" in msg_lower or "timed out" in msg_lower or "deadline exceeded" in msg_lower:
            return TIMEOUT
        elif "rate limit" in msg_lower or "429" in msg_lower or "quota exceeded" in msg_lower:
            return RATE_LIMIT
        elif "budget" in msg_lower or "cost limit" in msg_lower or "insufficient funds" in msg_lower:
            return BUDGET_EXCEEDED
        elif "unauthorized" in msg_lower or "forbidden" in msg_lower or "401" in msg_lower or "403" in msg_lower or "permission" in msg_lower:
            return AUTHORIZATION_FAILURE
        elif "rejected" in msg_lower or "approval denied" in msg_lower:
            return APPROVAL_REJECTED
        elif "tool" in msg_lower or component == "tool":
            return TOOL_FAILURE
        elif "mcp" in msg_lower or component == "mcp":
            return MCP_FAILURE
        elif "model" in msg_lower or "context window" in msg_lower or component in ["model", "llm"]:
            return MODEL_FAILURE
        elif "provider" in msg_lower or "502" in msg_lower or "503" in msg_lower:
            return PROVIDER_FAILURE
        elif "workflow" in msg_lower or component == "workflow":
            return WORKFLOW_FAILURE
        elif "agent" in msg_lower or component == "agent":
            return AGENT_FAILURE
        elif "memory" in msg_lower or component == "memory":
            return MEMORY_FAILURE
        elif "knowledge" in msg_lower or "vector" in msg_lower or component in ["knowledge", "rag"]:
            return KNOWLEDGE_FAILURE
        else:
            return SYSTEM_FAILURE

    def identify_failure_chain(self, spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Trace chronological dependency chain of error-emitting spans."""
        failed_spans = []
        for s in spans:
            status = s.get("status", "OK")
            attrs = s.get("attributes", {})
            if status.upper() in ["ERROR", "FAILED"] or attrs.get("error"):
                failed_spans.append({
                    "span_id": s.get("span_id"),
                    "name": s.get("name"),
                    "component": attrs.get("component") or s.get("name", "").split(".")[0],
                    "status_description": s.get("status_description") or attrs.get("error.message", "Unknown error"),
                    "start_time": s.get("start_time"),
                })
        # Sort by start_time ascending
        failed_spans.sort(key=lambda x: x.get("start_time", 0))
        return failed_spans

    def generate_recommendations(self, category: str, error_message: str) -> List[str]:
        """Produce actionable recommendations based on root cause category."""
        recs = []
        if category == TIMEOUT:
            recs.append("Increase timeout setting on target tool or model invocation.")
            recs.append("Consider breaking down long tasks into asynchronous workflow steps.")
        elif category == RATE_LIMIT:
            recs.append("Configure backoff and retry policy in provider load balancer.")
            recs.append("Request a quota increase for the target API model provider.")
        elif category == BUDGET_EXCEEDED:
            recs.append("Increase workspace budget limits or switch to a lower-cost model.")
        elif category == AUTHORIZATION_FAILURE:
            recs.append("Verify API key permissions or RBAC roles assigned to workspace.")
        elif category == TOOL_FAILURE:
            recs.append("Inspect tool parameters and schema validation rules.")
            recs.append("Verify network connectivity and credentials for external API endpoint.")
        elif category == MODEL_FAILURE:
            recs.append("Ensure prompt size does not exceed model context window limits.")
            recs.append("Fail over to an alternate model provider if degradation persists.")
        elif category == WORKFLOW_FAILURE:
            recs.append("Check node dependency logic and fallback retry handlers.")
        else:
            recs.append("Inspect detailed system logs and check system status.")
        return recs

    def analyze_failure(
        self,
        execution_id: str,
        spans: List[Dict[str, Any]],
        default_error: Optional[str] = None,
    ) -> FailureReport:
        """Perform comprehensive root cause analysis across trace spans."""
        failure_chain = self.identify_failure_chain(spans)

        if failure_chain:
            root_cause_span = failure_chain[0]
            root_span_id = root_cause_span["span_id"]
            root_msg = root_cause_span["status_description"]
            component = root_cause_span["component"]
        else:
            root_span_id = None
            root_msg = default_error or "Execution failed without explicit error span details."
            component = "general"

        category = self.identify_root_cause(root_msg, component)
        recommendations = self.generate_recommendations(category, root_msg)
        trace_id = spans[0].get("trace_id", "unknown") if spans else "unknown"

        return FailureReport(
            execution_id=execution_id,
            trace_id=trace_id,
            primary_category=category,
            root_cause_span_id=root_span_id,
            root_cause_message=root_msg,
            failure_chain=failure_chain,
            recommendations=recommendations,
        )
