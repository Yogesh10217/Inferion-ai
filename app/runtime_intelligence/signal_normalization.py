"""Signal normalization engine for Runtime Intelligence (Phase 5.57)."""

import hashlib
import json
import logging

from app.runtime_intelligence.models import NormalizedRuntimeSignal, RuntimeSignal

logger = logging.getLogger(__name__)


class RuntimeSignalNormalizer:
    """Normalizes multi-domain findings into canonical NormalizedRuntimeSignal format."""

    def normalize(self, signal: RuntimeSignal) -> NormalizedRuntimeSignal:
        domain = signal.metadata.source_domain if signal.metadata else "unknown"
        raw_str = json.dumps({"tenant": signal.tenant_id, "type": signal.signal_type.value, "payload": signal.payload}, sort_keys=True)
        fp = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

        normalized = NormalizedRuntimeSignal(
            tenant_id=signal.tenant_id,
            signal_id=signal.signal_id,
            normalized_type=signal.signal_type.value,
            normalized_severity=signal.severity.value,
            source_domain=domain,
            raw_payload=signal.payload,
            fingerprint=fp,
        )
        logger.debug(f"Normalized signal '{signal.signal_id}' -> Fingerprint {fp[:12]}")
        return normalized
