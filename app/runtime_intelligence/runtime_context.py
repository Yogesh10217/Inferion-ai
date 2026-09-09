"""Runtime context fusion builder for Runtime Intelligence (Phase 5.54)."""

import hashlib
import json
import logging
from typing import List
from app.runtime_intelligence.models import NormalizedRuntimeSignal, RuntimeContext

logger = logging.getLogger(__name__)


class RuntimeContextBuilder:
    """Fuses normalized signals into a bounded context window with SHA-256 fingerprinting."""

    def build_context(
        self,
        tenant_id: str,
        signals: List[NormalizedRuntimeSignal],
        bounded_window_minutes: int = 60,
        max_signals: int = 100,
    ) -> RuntimeContext:
        bounded_signals = signals[:max_signals]
        fingerprint_source = json.dumps(
            [{"id": s.signal_id, "fp": s.fingerprint} for s in bounded_signals],
            sort_keys=True,
        )
        ctx_fp = hashlib.sha256(fingerprint_source.encode("utf-8")).hexdigest()

        ctx = RuntimeContext(
            tenant_id=tenant_id,
            signals=bounded_signals,
            context_fingerprint=ctx_fp,
            bounded_window_minutes=bounded_window_minutes,
        )
        logger.info(f"Built RuntimeContext '{ctx.context_id}' with {len(bounded_signals)} signals (Fingerprint: {ctx_fp[:12]}...)")
        return ctx
