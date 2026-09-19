"""Zero-Trust Continuous Evaluation & Dynamic Risk Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TrustLevel(str, Enum):
    TRUSTED = "TRUSTED"
    LOW_RISK = "LOW_RISK"
    MEDIUM_RISK = "MEDIUM_RISK"
    HIGH_RISK = "HIGH_RISK"
    UNTRUSTED = "UNTRUSTED"


class ZeroTrustAction(str, Enum):
    ALLOW = "ALLOW"
    MONITOR = "MONITOR"
    CHALLENGE = "CHALLENGE"
    REQUIRE_MFA = "REQUIRE_MFA"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"
    TERMINATE_SESSION = "TERMINATE_SESSION"


class TrustEvaluation(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"zt_{uuid.uuid4().hex[:10]}")
    identity_id: str
    tenant_id: str = "global"

    trust_level: TrustLevel = TrustLevel.TRUSTED
    recommended_action: ZeroTrustAction = ZeroTrustAction.ALLOW
    trust_score: float = 100.0  # 0.0 to 100.0 scale

    contributing_signals: List[Dict[str, Any]] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=_now)


class ZeroTrustEngine:
    """Continuously evaluates identity, session context, network trust, and behavioral signals."""

    def evaluate(
        self,
        identity_id: str,
        tenant_id: str = "global",
        network_trusted: bool = True,
        device_trusted: bool = True,
        risk_score: float = 0.0,
        data_classification: str = "INTERNAL",
    ) -> TrustEvaluation:
        signals = []

        # 1. Evaluate risk inputs
        effective_trust = 100.0 - risk_score
        if not network_trusted:
            effective_trust -= 25.0
            signals.append({"signal": "UNTRUSTED_NETWORK", "impact": -25.0})
        if not device_trusted:
            effective_trust -= 20.0
            signals.append({"signal": "UNMANAGED_DEVICE", "impact": -20.0})

        effective_trust = float(max(0.0, min(100.0, effective_trust)))

        if effective_trust >= 80.0:
            level = TrustLevel.TRUSTED
            action = ZeroTrustAction.ALLOW
        elif effective_trust >= 60.0:
            level = TrustLevel.LOW_RISK
            action = ZeroTrustAction.MONITOR
        elif effective_trust >= 40.0:
            level = TrustLevel.MEDIUM_RISK
            action = ZeroTrustAction.REQUIRE_MFA
        elif effective_trust >= 20.0:
            level = TrustLevel.HIGH_RISK
            action = ZeroTrustAction.RESTRICT
        else:
            level = TrustLevel.UNTRUSTED
            action = ZeroTrustAction.TERMINATE_SESSION

        res = TrustEvaluation(
            identity_id=identity_id,
            tenant_id=tenant_id,
            trust_level=level,
            recommended_action=action,
            trust_score=effective_trust,
            contributing_signals=signals,
        )
        logger.info(
            f"[ZERO TRUST] Evaluated '{identity_id}' ({tenant_id}): Trust Score = {effective_trust:.1f} ({level.value}) -> Action = {action.value}"
        )
        return res
