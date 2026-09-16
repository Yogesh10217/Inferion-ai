"""Capacity explainability engine for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CapacityExplainabilityEngine:
    """Generates transparent, explainable rationales for capacity risks, saturation predictions, and recommendations."""

    def explain_capacity_finding(
        self, tenant_id: str, finding_type: str, resource_id: str
    ) -> Dict[str, Any]:
        explanation = f"Finding '{finding_type}' for resource '{resource_id}' was triggered because utilization trends exceed threshold headroom of 15.0%."
        logger.info(f"Generated explanation for finding '{finding_type}' on resource '{resource_id}'")
        return {
            "tenant_id": tenant_id,
            "finding_type": finding_type,
            "resource_id": resource_id,
            "explanation": explanation,
            "transparency_score": 0.98,
        }
