"""Tenant-Isolated Reliability Learning Subsystem (Phase 5.31)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantIsolationValidator


class ReliabilityPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"pat_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    pattern_name: str
    description: str
    recurrence_count: int = 1
    recommended_mitigation: str
    learned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReliabilityLearningManager:
    """Extracts tenant-isolated reliability learning insights from postmortems and incidents."""

    def __init__(self) -> None:
        self._patterns: Dict[str, ReliabilityPattern] = {}

    def record_learning(
        self,
        tenant_id: str,
        pattern_name: str,
        description: str,
        recommended_mitigation: str,
    ) -> ReliabilityPattern:
        pat = ReliabilityPattern(
            tenant_id=tenant_id,
            pattern_name=pattern_name,
            description=description,
            recommended_mitigation=recommended_mitigation,
        )
        self._patterns[pat.pattern_id] = pat
        return pat

    def list_patterns(self, tenant_id: str) -> List[ReliabilityPattern]:
        return [p for p in self._patterns.values() if p.tenant_id == tenant_id]
