"""
Workflow Failure Handling Subsystem.
Classifies workflow failure modes and routes failure resolution paths.
"""

from enum import Enum
from typing import Optional


class FailureClassification(str, Enum):
    TRANSIENT = "TRANSIENT"
    PERMANENT = "PERMANENT"
    DEPENDENCY = "DEPENDENCY"
    POLICY = "POLICY"
    APPROVAL = "APPROVAL"
    VERIFICATION = "VERIFICATION"
    UNKNOWN = "UNKNOWN"


class WorkflowFailureHandler:
    """Classifies workflow step and execution failures."""

    def classify_failure(self, error_message: str, error_code: Optional[str] = None) -> FailureClassification:
        msg = error_message.upper()
        if "TIMEOUT" in msg or "TRANSIENT" in msg or "503" in msg:
            return FailureClassification.TRANSIENT
        elif "DEPENDENCY" in msg or "CYCLE" in msg:
            return FailureClassification.DEPENDENCY
        elif "POLICY" in msg or "DENIED" in msg or "BOUNDARY" in msg:
            return FailureClassification.POLICY
        elif "APPROVAL" in msg or "REJECTED" in msg:
            return FailureClassification.APPROVAL
        elif "VERIFICATION" in msg or "HEALTH_CHECK" in msg:
            return FailureClassification.VERIFICATION
        return FailureClassification.PERMANENT
