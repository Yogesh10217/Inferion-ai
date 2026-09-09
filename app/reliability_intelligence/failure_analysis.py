"""Failure classification and pattern analysis engine (Phase 5.55)."""

import logging
from typing import Dict, Any, List
from app.reliability_intelligence.models import FailureClassification

logger = logging.getLogger(__name__)


class FailureAnalysisEngine:
    """Classifies failure events into TRANSIENT, PERMANENT, INTERMITTENT, DEPENDENCY, CAPACITY, etc."""

    def classify_failure(self, failure_payload: Dict[str, Any]) -> FailureClassification:
        error_msg = str(failure_payload.get("error", "")).lower()

        if "timeout" in error_msg or "transient" in error_msg:
            return FailureClassification.TRANSIENT
        elif "connection refused" in error_msg or "dependency" in error_msg:
            return FailureClassification.DEPENDENCY
        elif "oom" in error_msg or "capacity" in error_msg or "quota" in error_msg:
            return FailureClassification.CAPACITY
        else:
            return FailureClassification.PERMANENT
