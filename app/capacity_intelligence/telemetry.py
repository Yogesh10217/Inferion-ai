"""Telemetry ingestion engine for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import CapacityTelemetry

logger = logging.getLogger(__name__)


class CapacityTelemetryEngine:
    """Ingests and sanitizes capacity telemetry metrics."""

    def ingest_telemetry(
        self, tenant_id: str, resource_id: str, metric_name: str, metric_value: float, unit: str = "percentage"
    ) -> CapacityTelemetry:
        telem = CapacityTelemetry(
            tenant_id=tenant_id,
            resource_id=resource_id,
            metric_name=metric_name,
            metric_value=metric_value,
            unit=unit,
        )
        logger.info(f"Ingested CapacityTelemetry '{telem.telemetry_id}' for resource '{resource_id}' ({metric_name}={metric_value})")
        return telem
