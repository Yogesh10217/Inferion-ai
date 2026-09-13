from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from app.deployment.exceptions import IllegalStateTransitionError
from app.deployment.models import ProductionDeploymentState
from app.deployment.secrets import SecretsSanitizer


@dataclass
class ProductionDeploymentStateTransition:
    previous_state: ProductionDeploymentState
    next_state: ProductionDeploymentState
    timestamp: str
    reason: str
    evidence_level: str
    fingerprint: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "previous_state": self.previous_state.value,
            "next_state": self.next_state.value,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "evidence_level": self.evidence_level,
            "fingerprint": self.fingerprint,
            "metadata": self.metadata,
        })


class ProductionDeploymentStateMachine:
    """Deterministic state machine governing Phase 5.67 production deployment execution."""

    ALLOWED_TRANSITIONS: Dict[ProductionDeploymentState, Set[ProductionDeploymentState]] = {
        ProductionDeploymentState.NOT_EXECUTED: {
            ProductionDeploymentState.AUTHORIZATION_REQUIRED,
            ProductionDeploymentState.PREFLIGHT_VALIDATING,
        },
        ProductionDeploymentState.AUTHORIZATION_REQUIRED: {
            ProductionDeploymentState.AUTHORIZED,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.AUTHORIZED: {
            ProductionDeploymentState.PREFLIGHT_VALIDATING,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.PREFLIGHT_VALIDATING: {
            ProductionDeploymentState.ARTIFACT_VERIFYING,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.ARTIFACT_VERIFYING: {
            ProductionDeploymentState.INFRASTRUCTURE_VALIDATING,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.INFRASTRUCTURE_VALIDATING: {
            ProductionDeploymentState.DATABASE_VALIDATING,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.DATABASE_VALIDATING: {
            ProductionDeploymentState.BACKUP_VALIDATING,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.BACKUP_VALIDATING: {
            ProductionDeploymentState.DEPLOYMENT_PREPARING,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.DEPLOYMENT_PREPARING: {
            ProductionDeploymentState.DEPLOYMENT_EXECUTING,
            ProductionDeploymentState.FAILED,
        },
        ProductionDeploymentState.DEPLOYMENT_EXECUTING: {
            ProductionDeploymentState.DEPLOYMENT_STARTING,
            ProductionDeploymentState.FAILED,
            ProductionDeploymentState.ROLLBACK_REQUIRED,
        },
        ProductionDeploymentState.DEPLOYMENT_STARTING: {
            ProductionDeploymentState.HEALTH_VALIDATING,
            ProductionDeploymentState.FAILED,
            ProductionDeploymentState.ROLLBACK_REQUIRED,
        },
        ProductionDeploymentState.HEALTH_VALIDATING: {
            ProductionDeploymentState.SMOKE_TESTING,
            ProductionDeploymentState.FAILED,
            ProductionDeploymentState.ROLLBACK_REQUIRED,
        },
        ProductionDeploymentState.SMOKE_TESTING: {
            ProductionDeploymentState.TRAFFIC_VALIDATING,
            ProductionDeploymentState.FAILED,
            ProductionDeploymentState.ROLLBACK_REQUIRED,
        },
        ProductionDeploymentState.TRAFFIC_VALIDATING: {
            ProductionDeploymentState.RUNTIME_VALIDATING,
            ProductionDeploymentState.FAILED,
            ProductionDeploymentState.ROLLBACK_REQUIRED,
        },
        ProductionDeploymentState.RUNTIME_VALIDATING: {
            ProductionDeploymentState.DEPLOYMENT_VALIDATED,
            ProductionDeploymentState.FAILED,
            ProductionDeploymentState.ROLLBACK_REQUIRED,
            ProductionDeploymentState.VALIDATION_FAILED,
        },
        ProductionDeploymentState.DEPLOYMENT_VALIDATED: set(),
        ProductionDeploymentState.FAILED: {
            ProductionDeploymentState.ROLLBACK_REQUIRED,
        },
        ProductionDeploymentState.ROLLBACK_REQUIRED: {
            ProductionDeploymentState.ROLLBACK_EXECUTING,
        },
        ProductionDeploymentState.ROLLBACK_EXECUTING: {
            ProductionDeploymentState.ROLLBACK_VALIDATING,
        },
        ProductionDeploymentState.ROLLBACK_VALIDATING: {
            ProductionDeploymentState.ROLLED_BACK,
        },
        ProductionDeploymentState.ROLLED_BACK: set(),
        ProductionDeploymentState.VALIDATION_FAILED: {
            ProductionDeploymentState.ROLLBACK_REQUIRED,
        },
    }

    def __init__(self, initial_state: ProductionDeploymentState = ProductionDeploymentState.NOT_EXECUTED) -> None:
        self.current_state = initial_state
        self.history: List[ProductionDeploymentStateTransition] = []

    def transition_to(
        self,
        target_state: ProductionDeploymentState,
        reason: str,
        evidence_level: str = "STATIC",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ProductionDeploymentStateTransition:
        allowed = self.ALLOWED_TRANSITIONS.get(self.current_state, set())
        if target_state not in allowed:
            err = f"ILLEGAL_STATE_TRANSITION: Cannot transition deployment state from '{self.current_state.value}' to '{target_state.value}'"
            raise IllegalStateTransitionError(err)

        prev = self.current_state
        self.current_state = target_state
        now = datetime.now(timezone.utc).isoformat()

        payload = {
            "from": prev.value,
            "to": target_state.value,
            "timestamp": now,
            "reason": reason,
            "evidence_level": evidence_level,
        }
        fp = f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"

        transition = ProductionDeploymentStateTransition(
            previous_state=prev,
            next_state=target_state,
            timestamp=now,
            reason=reason,
            evidence_level=evidence_level,
            fingerprint=fp,
            metadata=metadata or {},
        )
        self.history.append(transition)
        return transition
