"""Runtime Action Boundary Engine for Phase 5.57 Runtime Intelligence."""

import logging
from enum import Enum

logger = logging.getLogger(__name__)


class ActionSafetyClassification(str, Enum):
    ADVISORY_ONLY = "ADVISORY_ONLY"
    AUTONOMOUS_ALLOWED = "AUTONOMOUS_ALLOWED"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    PROHIBITED = "PROHIBITED"


class RuntimeBoundaryEngine:
    """Classifies runtime adaptation actions into strict safety boundary levels."""

    ACTION_SAFETY_MAP = {
        "TELEMETRY_COLLECTION": ActionSafetyClassification.ADVISORY_ONLY,
        "RECOMMENDATION_GENERATION": ActionSafetyClassification.ADVISORY_ONLY,
        "SCALE_SERVICE": ActionSafetyClassification.APPROVAL_REQUIRED,
        "RESTART_PRODUCTION_SERVICE": ActionSafetyClassification.APPROVAL_REQUIRED,
        "TRAFFIC_MIGRATION": ActionSafetyClassification.APPROVAL_REQUIRED,
        "DATABASE_FAILOVER": ActionSafetyClassification.APPROVAL_REQUIRED,
        "DIRECT_INFRASTRUCTURE_MUTATION": ActionSafetyClassification.PROHIBITED,
        "MODIFY_IAM_PERMISSIONS": ActionSafetyClassification.PROHIBITED,
    }

    def classify_action(self, action_name: str) -> ActionSafetyClassification:
        normalized = action_name.strip().upper()
        classification = self.ACTION_SAFETY_MAP.get(normalized, ActionSafetyClassification.APPROVAL_REQUIRED)
        logger.info(f"Classified runtime action '{action_name}' as {classification.value}")
        return classification
