"""Threat Indicators & IOC Intelligence Management."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field


class ThreatIndicator(BaseModel):
    indicator_id: str = Field(default_factory=lambda: f"ioc-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    type: str  # IP, HASH, PATTERN, USER_AGENT, PROMPT_KEYWORD
    value: str
    confidence: float = 0.9  # 0.0 to 1.0
    source: str = "threat-intel-feed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ThreatIndicatorManager:
    """Manages Indicators of Compromise (IOC) feeds and matching."""

    def __init__(self) -> None:
        self._indicators: Dict[str, ThreatIndicator] = {}

    def add_indicator(
        self,
        tenant_id: str,
        type: str,
        value: str,
        confidence: float = 0.9,
        source: str = "threat-intel-feed",
    ) -> ThreatIndicator:
        indicator = ThreatIndicator(
            tenant_id=tenant_id,
            type=type,
            value=value,
            confidence=confidence,
            source=source,
        )
        self._indicators[indicator.indicator_id] = indicator
        return indicator

    def list_indicators(self, tenant_id: str) -> List[ThreatIndicator]:
        return [i for i in self._indicators.values() if i.tenant_id == tenant_id]

    def match_payload(self, tenant_id: str, text: str) -> List[ThreatIndicator]:
        matches = []
        indicators = self.list_indicators(tenant_id)
        for ind in indicators:
            if ind.value in text:
                matches.append(ind)
        return matches
