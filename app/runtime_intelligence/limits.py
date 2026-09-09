"""Runtime Limits Manager for Phase 5.57 Runtime Intelligence."""

import logging
from typing import Dict, Any, List
from app.runtime_intelligence.exceptions import RuntimeIntelligenceLimitExceededException

logger = logging.getLogger(__name__)


class RuntimeLimitsManager:
    """Enforces execution limits for runtime signals, context items, and evidence size."""

    MAX_SIGNALS = 1000
    MAX_CONTEXT_ITEMS = 500
    MAX_EVIDENCE_SIZE_KB = 512

    @classmethod
    def validate_signals_limit(cls, signal_count: int) -> None:
        if signal_count > cls.MAX_SIGNALS:
            raise RuntimeIntelligenceLimitExceededException(f"Signal count {signal_count} exceeds max {cls.MAX_SIGNALS}")

    @classmethod
    def validate_context_limit(cls, item_count: int) -> None:
        if item_count > cls.MAX_CONTEXT_ITEMS:
            raise RuntimeIntelligenceLimitExceededException(f"Context item count {item_count} exceeds max {cls.MAX_CONTEXT_ITEMS}")
