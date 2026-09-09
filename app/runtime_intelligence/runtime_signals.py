"""Runtime signal manager for Runtime Intelligence (Phase 5.54)."""

import logging
from typing import Dict, Any, List, Optional
from app.runtime_intelligence.models import (
    RuntimeSignal,
    RuntimeSignalType,
    RuntimeSignalSeverity,
    RuntimeSignalMetadata,
)
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class RuntimeSignalEngine:
    """Ingests and validates sanitized runtime signals."""

    def ingest_signal(
        self,
        tenant_id: str,
        signal_type: str,
        severity: str,
        payload: Dict[str, Any],
        source_domain: str = "operations",
    ) -> RuntimeSignal:
        clean_payload = SensitiveDataSanitizer.sanitize(payload)
        sType = RuntimeSignalType[signal_type.upper()] if signal_type.upper() in RuntimeSignalType.__members__ else RuntimeSignalType.HEALTH
        sSev = RuntimeSignalSeverity[severity.upper()] if severity.upper() in RuntimeSignalSeverity.__members__ else RuntimeSignalSeverity.INFO

        sig = RuntimeSignal(
            tenant_id=tenant_id,
            signal_type=sType,
            severity=sSev,
            payload=clean_payload,
            metadata=RuntimeSignalMetadata(source_domain=source_domain, component_id=f"comp_{source_domain}"),
        )
        logger.info(f"Ingested RuntimeSignal '{sig.signal_id}' for tenant '{tenant_id}' (Type: {sType.value}, Sev: {sSev.value})")
        return sig
