"""Signal Normalization Engine for Phase 5.51 Enterprise AI Unified Intelligence."""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.normalization_contracts import UnifiedDomainInput, NormalizedSignal
from app.platform_contracts.redaction import SensitiveDataSanitizer

logger = logging.getLogger(__name__)


class SignalNormalizationEngine:
    """Normalizes cross-domain inputs into standardized NormalizedSignals."""

    def __init__(self) -> None:
        self.sanitizer = SensitiveDataSanitizer()

    def normalize_input(self, domain_input: UnifiedDomainInput) -> NormalizedSignal:
        raw_meta = getattr(domain_input, 'raw_metadata', None) or getattr(domain_input, 'metadata', {})
        sanitized_payload = self.sanitizer.sanitize_copy(raw_meta)

        sig_id = f"norm-sig-{uuid.uuid4().hex[:8]}"
        corr_id = f"corr-{uuid.uuid4().hex[:8]}"
        conf = domain_input.effective_confidence

        return NormalizedSignal(
            signal_id=sig_id,
            correlation_id=corr_id,
            domain=domain_input.domain,
            tenant_id=domain_input.tenant_id,
            entity_reference=domain_input.entity_reference,
            signal_type=domain_input.signal_type,
            severity=domain_input.severity,
            confidence_score=conf,
            risk_score=domain_input.risk_score,
            evidence_ids=domain_input.evidence_references,
            sanitized_payload=sanitized_payload
        )

    def normalize(self, domain_input: UnifiedDomainInput) -> NormalizedSignal:
        return self.normalize_input(domain_input)


# Alias for backward compatibility
SignalNormalizer = SignalNormalizationEngine
