"""Blast radius analyzer for Reliability Intelligence (Phase 5.55)."""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class BlastRadiusAnalyzer:
    """Evaluates blast radius across services, users, tenants, regions, domains, data, models, and business."""

    def calculate_blast_radius(
        self, tenant_id: str, origin_service: str, affected_count: int
    ) -> Dict[str, Any]:
        severity = "CRITICAL" if affected_count > 5 else ("HIGH" if affected_count > 2 else "MEDIUM")
        return {
            "origin_service": origin_service,
            "tenant_id": tenant_id,
            "affected_services_count": affected_count,
            "blast_radius_severity": severity,
            "impacted_dimensions": ["services", "operations", "business", "data"],
        }
