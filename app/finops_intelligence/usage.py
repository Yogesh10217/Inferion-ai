"""Usage Intelligence & Telemetry (Phase 5.42)."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.finops_intelligence.exceptions import CrossTenantFinOpsIntelligenceException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class UsageDimension(BaseModel):
    key: str
    value: str


class UsageMetric(BaseModel):
    metric_name: str  # TOKENS, API_CALLS, EXECUTION_TIME_MS, STORAGE_BYTES
    metric_value: float


class UsageRecord(BaseModel):
    usage_id: str = Field(default_factory=lambda: f"usg_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_type: str  # MODEL, AGENT, INTEGRATION, INFRASTRUCTURE, WORKFLOW
    resource_id: str
    metrics: List[UsageMetric] = Field(default_factory=list)
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UsageAssessment(BaseModel):
    tenant_id: str
    total_tokens: float = 0.0
    total_api_calls: float = 0.0
    total_execution_ms: float = 0.0


class UsageIntelligenceManager:
    """Manages analytical usage telemetry with sensitive metadata sanitization."""

    def __init__(self) -> None:
        self._records: Dict[str, UsageRecord] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def record_usage(
        self,
        tenant_id: str,
        resource_type: str,
        resource_id: str,
        metrics: List[UsageMetric],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> UsageRecord:
        sanitized = self.sanitizer.sanitize(metadata or {})
        rec = UsageRecord(
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            metrics=metrics,
            sanitized_metadata=sanitized,
        )
        self._records[rec.usage_id] = rec
        return rec

    def evaluate_usage(self, tenant_id: str) -> UsageAssessment:
        records = [r for r in self._records.values() if r.tenant_id == tenant_id]
        tokens = 0.0
        calls = 0.0
        ms = 0.0

        for r in records:
            for m in r.metrics:
                if m.metric_name == "TOKENS":
                    tokens += m.metric_value
                elif m.metric_name == "API_CALLS":
                    calls += m.metric_value
                elif m.metric_name == "EXECUTION_TIME_MS":
                    ms += m.metric_value

        return UsageAssessment(
            tenant_id=tenant_id,
            total_tokens=tokens,
            total_api_calls=calls,
            total_execution_ms=ms,
        )

    def get_record(self, tenant_id: str, usage_id: str) -> UsageRecord:
        rec = self._records.get(usage_id)
        if not rec or rec.tenant_id != tenant_id:
            raise CrossTenantFinOpsIntelligenceException()
        return rec
