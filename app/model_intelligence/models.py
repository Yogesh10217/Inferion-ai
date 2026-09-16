"""Enterprise Model Reference Intelligence (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelReferenceNotFoundException

logger = logging.getLogger(__name__)


class ModelType(str, Enum):
    LLM = "LLM"
    EMBEDDING = "EMBEDDING"
    MULTIMODAL = "MULTIMODAL"
    CLASSIFICATION = "CLASSIFICATION"
    PREDICTION = "PREDICTION"
    RECOMMENDATION = "RECOMMENDATION"
    INTERNAL = "INTERNAL"
    EXTERNAL_PROVIDER = "EXTERNAL_PROVIDER"


class ModelStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    RETIRED = "RETIRED"
    EXPERIMENTAL = "EXPERIMENTAL"
    QUARANTINED = "QUARANTINED"


class ModelProviderReference(BaseModel):
    provider_id: str
    provider_name: str
    region: str = "us-east-1"
    endpoint_type: str = "API"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ModelCapabilityReference(BaseModel):
    capability_name: str
    supported: bool = True
    context_window: Optional[int] = None
    max_output_tokens: Optional[int] = None
    multimodal_types: List[str] = Field(default_factory=list)


class ModelVersionReference(BaseModel):
    version_id: str
    version_tag: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


class ModelDeploymentReference(BaseModel):
    deployment_id: str
    environment: str = "production"
    traffic_weight: float = 1.0
    status: str = "HEALTHY"


class ModelMetadata(BaseModel):
    description: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    owner: str = "system"
    cost_per_1k_input_tokens: float = 0.001
    cost_per_1k_output_tokens: float = 0.002
    extra: Dict[str, Any] = Field(default_factory=dict)


class ModelReference(BaseModel):
    model_id: str
    name: str
    tenant_id: str
    model_type: ModelType
    status: ModelStatus = ModelStatus.ACTIVE
    provider: ModelProviderReference
    current_version: ModelVersionReference
    capabilities: List[ModelCapabilityReference] = Field(default_factory=list)
    deployments: List[ModelDeploymentReference] = Field(default_factory=list)
    metadata: ModelMetadata = Field(default_factory=ModelMetadata)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelIntelligenceRegistry:
    """Read-only reference registry for model metadata without duplicating underlying storage."""

    def __init__(self) -> None:
        self._models: Dict[str, ModelReference] = {}

    def register_model(
        self,
        name: str,
        tenant_id: str,
        model_type: ModelType,
        provider: ModelProviderReference,
        version_tag: str = "1.0.0",
        metadata: Optional[ModelMetadata] = None,
        model_id: Optional[str] = None,
    ) -> ModelReference:
        m_id = model_id or f"model-{uuid.uuid4().hex[:8]}"
        version_ref = ModelVersionReference(version_id=f"ver-{uuid.uuid4().hex[:6]}", version_tag=version_tag)
        ref = ModelReference(
            model_id=m_id,
            name=name,
            tenant_id=tenant_id,
            model_type=model_type,
            provider=provider,
            current_version=version_ref,
            metadata=metadata or ModelMetadata(),
        )
        self._models[m_id] = ref
        logger.info(f"[MODEL INTELLIGENCE] Registered model reference {name} ({m_id}) for tenant {tenant_id}")
        return ref

    def get_model(self, model_id: str, tenant_id: str) -> ModelReference:
        model = self._models.get(model_id)
        if not model:
            raise ModelReferenceNotFoundException(f"Model '{model_id}' not found.")
        if model.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return model

    def list_models(self, tenant_id: str, model_type: Optional[ModelType] = None) -> List[ModelReference]:
        res = [m for m in self._models.values() if m.tenant_id == tenant_id]
        if model_type:
            res = [m for m in res if m.model_type == model_type]
        return res
