"""Runtime observation normalizer for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any
from app.continuous_assurance.models import RuntimeObservation, NormalizedRuntimeObservation
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class RuntimeObservationNormalizer:
    """Normalizes cross-domain runtime observations into standard schema."""

    def normalize(self, obs: RuntimeObservation) -> NormalizedRuntimeObservation:
        clean_payload = SensitiveDataSanitizer.sanitize(obs.payload)

        normalized = NormalizedRuntimeObservation(
            observation_id=obs.observation_id,
            tenant_id=obs.tenant_id,
            source_domain=obs.source_domain,
            normalized_type=obs.observation_type.value,
            severity=obs.severity.value,
            clean_payload=clean_payload,
            confidence=0.98,
        )

        logger.debug(f"Normalized observation '{obs.observation_id}' for domain '{obs.source_domain}'")
        return normalized
