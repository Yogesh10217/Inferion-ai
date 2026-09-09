"""Runtime observation processing engine for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any, Optional
from app.continuous_assurance.models import (
    RuntimeObservation,
    RuntimeObservationType,
    RuntimeObservationSeverity,
    RuntimeObservationStatus,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class RuntimeObservationManager:
    """Ingests and sanitizes raw runtime observations across enterprise domains."""

    def create_observation(
        self,
        tenant_id: str,
        source_domain: str,
        observation_type: str,
        payload: Dict[str, Any],
        severity: str = "INFO",
    ) -> RuntimeObservation:
        sanitized_payload = SensitiveDataSanitizer.sanitize(payload)

        try:
            obs_type = RuntimeObservationType(observation_type)
        except ValueError:
            obs_type = RuntimeObservationType.OPERATIONAL_EVENT

        try:
            sev = RuntimeObservationSeverity(severity)
        except ValueError:
            sev = RuntimeObservationSeverity.INFO

        obs = RuntimeObservation(
            tenant_id=tenant_id,
            source_domain=source_domain,
            observation_type=obs_type,
            severity=sev,
            payload=sanitized_payload,
            status=RuntimeObservationStatus.UNPROCESSED,
        )

        logger.info(f"Created sanitized RuntimeObservation '{obs.observation_id}' for tenant '{tenant_id}'")
        return obs
