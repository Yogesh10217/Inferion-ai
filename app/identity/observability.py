"""Identity & Access Management Prometheus Metrics Collector."""

import logging
from typing import Dict, Any, Optional

try:
    from prometheus_client import Counter, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)

if PROMETHEUS_AVAILABLE:
    IDENTITY_AUTH_TOTAL = Counter("ai_identity_authentication_total", "Total authentications", ["tenant_id", "status"])
    IDENTITY_AUTH_FAILED_TOTAL = Counter("ai_identity_authentication_failed_total", "Total failed authentications", ["tenant_id"])
    IDENTITY_AUTHZ_TOTAL = Counter("ai_identity_authorization_total", "Total authorization evaluations", ["tenant_id", "decision"])
    IDENTITY_AUTHZ_DENIED_TOTAL = Counter("ai_identity_authorization_denied_total", "Total authorization denials", ["tenant_id"])
    IDENTITY_PRIVILEGED_ACCESS_TOTAL = Counter("ai_identity_privileged_access_total", "Total JIT privileged access grants", ["tenant_id", "role"])
    IDENTITY_ACTIVE_SESSIONS = Gauge("ai_identity_active_sessions", "Active sessions count", ["tenant_id"])
    IDENTITY_RISK_EVENTS_TOTAL = Counter("ai_identity_risk_events_total", "Total behavioral risk events", ["tenant_id", "severity"])
    IDENTITY_STEP_UP_AUTH_TOTAL = Counter("ai_identity_step_up_auth_total", "Total step-up authentication challenges", ["tenant_id"])
    IDENTITY_TOKEN_REVOCATIONS_TOTAL = Counter("ai_identity_token_revocations_total", "Total token revocations", ["tenant_id"])
    IDENTITY_ZERO_TRUST_DECISIONS_TOTAL = Counter("ai_identity_zero_trust_decisions_total", "Total Zero-Trust evaluations", ["tenant_id", "action"])


class IdentityMetricsCollector:
    """Collects and exposes Prometheus metrics for the Identity Platform."""

    def record_authentication(self, tenant_id: str, success: bool) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                status = "SUCCESS" if success else "FAILED"
                IDENTITY_AUTH_TOTAL.labels(tenant_id=tenant_id, status=status).inc()
                if not success:
                    IDENTITY_AUTH_FAILED_TOTAL.labels(tenant_id=tenant_id).inc()
            except Exception:
                pass

    def record_authorization(self, tenant_id: str, decision: str) -> None:
        if PROMETHEUS_AVAILABLE:
            try:
                IDENTITY_AUTHZ_TOTAL.labels(tenant_id=tenant_id, decision=decision).inc()
                if decision != "ALLOW":
                    IDENTITY_AUTHZ_DENIED_TOTAL.labels(tenant_id=tenant_id).inc()
            except Exception:
                pass
