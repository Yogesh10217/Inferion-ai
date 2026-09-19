"""Feature Management & Experimentation Engine (Phase 5.22 - Component 5).

Provides feature flags and deterministic experimentation:
- Targeting context: tenant, organization, workspace, user, role, application, environment, device, risk, subscription
- Deterministic variant assignment using: hash(tenant_id + user_id + experiment_id)
- Experiment states: CONTROL, TREATMENT, PAUSED, COMPLETED, ROLLED_BACK
"""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class FeatureState(str, Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    TENANT_TARGETED = "TENANT_TARGETED"
    USER_TARGETED = "USER_TARGETED"
    ROLE_TARGETED = "ROLE_TARGETED"
    PERCENTAGE_ROLLOUT = "PERCENTAGE_ROLLOUT"
    EXPERIMENT = "EXPERIMENT"


class ExperimentState(str, Enum):
    CONTROL = "CONTROL"
    TREATMENT = "TREATMENT"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    ROLLED_BACK = "ROLLED_BACK"


class FeatureVariant(BaseModel):
    """Variant definition for feature flags or experiments."""

    variant_id: str
    name: str
    weight_percentage: float = 50.0
    payload: Dict[str, Any] = Field(default_factory=dict)


class FeatureTargetingRule(BaseModel):
    """Targeting rule for feature flags."""

    rule_id: str = Field(default_factory=lambda: f"rule_{uuid.uuid4().hex[:12]}")
    tenants: List[str] = Field(default_factory=list)
    users: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    environments: List[str] = Field(default_factory=list)
    percentage: float = 100.0


class FeatureExperiment(BaseModel):
    """A/B experiment configuration."""

    experiment_id: str = Field(default_factory=lambda: f"exp_{uuid.uuid4().hex[:12]}")
    feature_key: str
    application_id: str
    tenant_id: str
    state: ExperimentState = ExperimentState.CONTROL
    variants: List[FeatureVariant] = Field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeatureFlag(BaseModel):
    """Feature flag definition."""

    flag_id: str = Field(default_factory=lambda: f"ff_{uuid.uuid4().hex[:12]}")
    feature_key: str
    application_id: str
    tenant_id: str
    state: FeatureState = FeatureState.DISABLED
    default_value: Any = False
    targeting_rule: Optional[FeatureTargetingRule] = None
    experiment: Optional[FeatureExperiment] = None
    variants: List[FeatureVariant] = Field(default_factory=list)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FeatureManager:
    """Manages feature flag creation, experimentation, and deterministic rule evaluation."""

    def __init__(self) -> None:
        self._flags: Dict[str, FeatureFlag] = {}  # key: f"{tenant_id}:{app_id}:{feature_key}"

    def create_flag(
        self,
        tenant_id: str,
        application_id: str,
        feature_key: str,
        state: FeatureState = FeatureState.ENABLED,
        default_value: Any = True,
        targeting_rule: Optional[FeatureTargetingRule] = None,
        variants: Optional[List[FeatureVariant]] = None,
    ) -> FeatureFlag:
        key = f"{tenant_id}:{application_id}:{feature_key}"
        flag = FeatureFlag(
            feature_key=feature_key,
            application_id=application_id,
            tenant_id=tenant_id,
            state=state,
            default_value=default_value,
            targeting_rule=targeting_rule,
            variants=variants or [],
        )
        self._flags[key] = flag
        logger.info(f"[FEATURE MANAGER] Created flag '{feature_key}' for app '{application_id}' (tenant '{tenant_id}')")
        return flag

    def create_experiment(
        self,
        tenant_id: str,
        application_id: str,
        feature_key: str,
        variants: List[FeatureVariant],
    ) -> FeatureExperiment:
        key = f"{tenant_id}:{application_id}:{feature_key}"
        exp = FeatureExperiment(
            feature_key=feature_key,
            application_id=application_id,
            tenant_id=tenant_id,
            state=ExperimentState.TREATMENT,
            variants=variants,
            start_time=datetime.now(timezone.utc),
        )

        if key in self._flags:
            self._flags[key].state = FeatureState.EXPERIMENT
            self._flags[key].experiment = exp
        else:
            self.create_flag(
                tenant_id=tenant_id,
                application_id=application_id,
                feature_key=feature_key,
                state=FeatureState.EXPERIMENT,
            )
            self._flags[key].experiment = exp

        return exp

    def evaluate_feature(
        self,
        tenant_id: str,
        application_id: str,
        feature_key: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluate feature flag or experiment for a given request context."""
        key = f"{tenant_id}:{application_id}:{feature_key}"
        if key not in self._flags:
            return {"feature_key": feature_key, "enabled": False, "variant": None, "reason": "FLAG_NOT_FOUND"}

        flag = self._flags[key]

        if flag.state == FeatureState.DISABLED:
            return {"feature_key": feature_key, "enabled": False, "variant": None, "reason": "DISABLED"}

        if flag.state == FeatureState.ENABLED:
            return {"feature_key": feature_key, "enabled": True, "variant": "default", "reason": "ENABLED"}

        # Experimentation Deterministic Hash Assignment
        if flag.state == FeatureState.EXPERIMENT and flag.experiment:
            exp = flag.experiment
            if exp.state in {ExperimentState.PAUSED, ExperimentState.ROLLED_BACK}:
                return {
                    "feature_key": feature_key,
                    "enabled": False,
                    "variant": "control",
                    "reason": f"EXPERIMENT_{exp.state.value}",
                }

            user_id = context.get("user_id", "anonymous")
            hash_input = f"{tenant_id}:{user_id}:{exp.experiment_id}"
            hash_val = int(hashlib.md5(hash_input.encode("utf-8"), usedforsecurity=False).hexdigest(), 16) % 100

            # Assign variant based on hash value
            assigned_variant = exp.variants[0] if exp.variants else None
            accumulated = 0.0
            for v in exp.variants:
                accumulated += v.weight_percentage
                if hash_val < accumulated:
                    assigned_variant = v
                    break

            return {
                "feature_key": feature_key,
                "enabled": True,
                "variant": assigned_variant.variant_id if assigned_variant else "control",
                "variant_payload": assigned_variant.payload if assigned_variant else {},
                "experiment_id": exp.experiment_id,
                "reason": "EXPERIMENT_DETERMINISTIC_ASSIGNMENT",
            }

        # Targeting Rule Evaluation
        if flag.targeting_rule:
            rule = flag.targeting_rule
            user_id = context.get("user_id")
            role = context.get("role")
            env = context.get("environment")

            if rule.tenants and tenant_id not in rule.tenants:
                return {"feature_key": feature_key, "enabled": False, "reason": "TENANT_MISMATCH"}

            if rule.users and user_id not in rule.users:
                return {"feature_key": feature_key, "enabled": False, "reason": "USER_NOT_TARGETED"}

            if rule.roles and role not in rule.roles:
                return {"feature_key": feature_key, "enabled": False, "reason": "ROLE_NOT_TARGETED"}

            if rule.environments and env not in rule.environments:
                return {"feature_key": feature_key, "enabled": False, "reason": "ENV_NOT_TARGETED"}

            return {
                "feature_key": feature_key,
                "enabled": True,
                "variant": "targeted",
                "reason": "TARGETING_RULE_MATCH",
            }

        return {"feature_key": feature_key, "enabled": flag.default_value, "reason": "DEFAULT"}
