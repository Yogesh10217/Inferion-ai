"""Capacity reproducibility record for Capacity Intelligence (Phase 5.56)."""

import hashlib
import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CapacityReproducibilityRecord:
    """Captures telemetry fingerprints and forecasting configurations for deterministic evaluation reproducibility."""

    def create_reproducibility_record(self, tenant_id: str, forecast_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        raw = json.dumps({"tenant": tenant_id, "forecast": forecast_id, "inputs": inputs}, sort_keys=True)
        fp = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        return {"tenant_id": tenant_id, "forecast_id": forecast_id, "reproducibility_hash": fp}
