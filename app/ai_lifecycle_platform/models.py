"""Model Registry & Lifecycle Metadata Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import (
    CrossTenantLifecycleAccessException,
    InvalidLifecycleTransitionException,
    ModelNotFoundException,
)
from app.platform_contracts.lifecycle import LifecycleMachine, LifecycleTransition


class ModelType(str, Enum):
    LLM = "LLM"
    CLASSIFIER = "CLASSIFIER"
    EMBEDDING = "EMBEDDING"
    MULTIMODAL = "MULTIMODAL"
    REASONING = "REASONING"


class ModelFramework(str, Enum):
    PYTORCH = "PYTORCH"
    TENSORFLOW = "TENSORFLOW"
    TRANSFORMERS = "TRANSFORMERS"
    ONNX = "ONNX"
    VLLM = "VLLM"
    CUSTOM = "CUSTOM"


class ModelStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DEPRECATED = "DEPRECATED"


class ModelLifecycleStage(str, Enum):
    REGISTERED = "REGISTERED"
    DEVELOPMENT = "DEVELOPMENT"
    VALIDATION = "VALIDATION"
    CANDIDATE = "CANDIDATE"
    APPROVED = "APPROVED"
    DEPLOYED = "DEPLOYED"
    MONITORING = "MONITORING"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class ModelArtifactReference(BaseModel):
    artifact_id: str
    artifact_type: str = "MODEL_BINARY"
    uri: str = "s3://models/weights.bin"


class ModelVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: f"mver_{uuid.uuid4().hex[:12]}")
    version_tag: str = "1.0.0"
    stage: ModelLifecycleStage = ModelLifecycleStage.REGISTERED
    dataset_version_ids: List[str] = Field(default_factory=list)
    artifacts: List[ModelArtifactReference] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIModel(BaseModel):
    model_id: str = Field(default_factory=lambda: f"mdl_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    model_type: ModelType = ModelType.LLM
    framework: ModelFramework = ModelFramework.TRANSFORMERS
    status: ModelStatus = ModelStatus.ACTIVE
    current_stage: ModelLifecycleStage = ModelLifecycleStage.REGISTERED
    versions: List[ModelVersion] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelManager:
    """Manages AI Model lifecycle metadata and version transitions."""

    def __init__(self) -> None:
        self._models: Dict[str, AIModel] = {}
        self.lifecycle_machine = LifecycleMachine(
            name="ModelLifecycle",
            initial_state=ModelLifecycleStage.REGISTERED.value,
            valid_transitions=[
                LifecycleTransition(from_state="REGISTERED", to_state="DEVELOPMENT"),
                LifecycleTransition(from_state="DEVELOPMENT", to_state="VALIDATION"),
                LifecycleTransition(from_state="VALIDATION", to_state="CANDIDATE"),
                LifecycleTransition(from_state="CANDIDATE", to_state="APPROVED"),
                LifecycleTransition(from_state="APPROVED", to_state="DEPLOYED"),
                LifecycleTransition(from_state="DEPLOYED", to_state="MONITORING"),
                LifecycleTransition(from_state="MONITORING", to_state="SUSPENDED"),
                LifecycleTransition(from_state="MONITORING", to_state="RETIRED"),
                LifecycleTransition(from_state="SUSPENDED", to_state="MONITORING"),
                LifecycleTransition(from_state="SUSPENDED", to_state="RETIRED"),
            ],
            terminal_states={"RETIRED"},
        )

    def register_model(
        self,
        tenant_id: str,
        name: str,
        model_type: ModelType = ModelType.LLM,
        framework: ModelFramework = ModelFramework.TRANSFORMERS,
        version_tag: str = "1.0.0",
        dataset_version_ids: Optional[List[str]] = None,
    ) -> AIModel:
        mver = ModelVersion(version_tag=version_tag, dataset_version_ids=dataset_version_ids or [])
        mdl = AIModel(
            tenant_id=tenant_id,
            name=name,
            model_type=model_type,
            framework=framework,
            versions=[mver],
        )
        self._models[mdl.model_id] = mdl
        return mdl

    def transition_stage(
        self,
        model_id: str,
        tenant_id: str,
        target_stage: ModelLifecycleStage,
    ) -> AIModel:
        mdl = self.get_model(model_id, tenant_id)
        try:
            self.lifecycle_machine.validate_transition(mdl.current_stage.value, target_stage.value)
        except Exception as e:
            raise InvalidLifecycleTransitionException(mdl.current_stage.value, target_stage.value) from e

        mdl.current_stage = target_stage
        if mdl.versions:
            mdl.versions[-1].stage = target_stage
        return mdl

    def get_model(self, model_id: str, tenant_id: str) -> AIModel:
        mdl = self._models.get(model_id)
        if not mdl:
            raise ModelNotFoundException(model_id)
        if tenant_id != "global" and mdl.tenant_id != "global" and tenant_id != mdl.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, mdl.tenant_id)
        return mdl

    def list_models(self, tenant_id: str) -> List[AIModel]:
        return [m for m in self._models.values() if m.tenant_id == tenant_id]
