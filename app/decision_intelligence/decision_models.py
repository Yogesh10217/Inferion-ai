"""
Decision Models Subsystem.
Defines machine learning / heuristic decision model configurations, scoring versions, and weight matrices.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class DecisionModelConfig(BaseModel):
    model_id: str = Field(default_factory=lambda: f"decmod_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str = "DeterministicEnterpriseDecisionModel"
    version: str = "1.0.0"
    weights: Dict[str, float] = Field(
        default_factory=lambda: {
            "security_risk": 0.3,
            "operational_impact": 0.25,
            "policy_compliance": 0.25,
            "cost_efficiency": 0.1,
            "evidence_quality": 0.1,
        }
    )
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionModelRegistry:
    """Registry for decision model versions and scoring matrices."""

    def __init__(self) -> None:
        self._models: Dict[str, DecisionModelConfig] = {}

    def register_model(self, tenant_id: str, name: str, version: str = "1.0.0", weights: Optional[Dict[str, float]] = None) -> DecisionModelConfig:
        config = DecisionModelConfig(tenant_id=tenant_id, name=name, version=version, weights=weights or {})
        self._models[config.model_id] = config
        return config

    def get_default_model(self, tenant_id: str) -> DecisionModelConfig:
        for mod in self._models.values():
            if mod.tenant_id == tenant_id and mod.is_active:
                return mod
        return DecisionModelConfig(tenant_id=tenant_id)
