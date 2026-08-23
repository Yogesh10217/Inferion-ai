"""Application Composition Engine (Phase 5.22 - Component 2).

Allows composing platform primitives (models, agents, teams, workflows, knowledge sources, memory, tools, integrations, prompts, policies, human tasks) into coherent AI applications without duplicating infrastructure logic.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.application_platform.exceptions import ResourceBindingException

logger = logging.getLogger(__name__)


class ComponentType(str, Enum):
    AI_MODEL = "AI_MODEL"
    AGENT = "AGENT"
    AGENT_TEAM = "AGENT_TEAM"
    WORKFLOW = "WORKFLOW"
    ORCHESTRATION_WORKFLOW = "ORCHESTRATION_WORKFLOW"
    KNOWLEDGE_SOURCE = "KNOWLEDGE_SOURCE"
    MEMORY_SCOPE = "MEMORY_SCOPE"
    TOOL = "TOOL"
    INTEGRATION = "INTEGRATION"
    PROMPT = "PROMPT"
    POLICY = "POLICY"
    HUMAN_TASK = "HUMAN_TASK"


class ComponentBinding(BaseModel):
    """Binding reference linking a composition component to an existing platform primitive."""

    binding_id: str = Field(default_factory=lambda: f"bind_{uuid.uuid4().hex[:12]}")
    resource_type: ComponentType
    resource_id: str
    resource_version: Optional[str] = None
    required: bool = True
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ApplicationComponent(BaseModel):
    """A logical component inside an application composition."""

    component_id: str = Field(default_factory=lambda: f"cmp_{uuid.uuid4().hex[:12]}")
    name: str
    component_type: ComponentType
    description: str = ""
    binding: ComponentBinding
    enabled: bool = True
    sequence_order: int = 0
    depends_on: List[str] = Field(default_factory=list)


class ApplicationComposition(BaseModel):
    """Composition specification for an AI Application."""

    composition_id: str = Field(default_factory=lambda: f"comp_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    name: str
    description: str = ""
    components: List[ApplicationComponent] = Field(default_factory=list)
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ApplicationCompositionManager:
    """Manages creation, resolution, and validation of application compositions."""

    def __init__(self) -> None:
        self._compositions: Dict[str, ApplicationComposition] = {}

    def create_composition(
        self,
        application_id: str,
        tenant_id: str,
        name: str,
        description: str = "",
        components: Optional[List[ApplicationComponent]] = None,
    ) -> ApplicationComposition:
        comp = ApplicationComposition(
            application_id=application_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            components=components or [],
        )
        self._compositions[comp.composition_id] = comp
        logger.info(f"[COMPOSITION MANAGER] Created composition {comp.composition_id} for app {application_id}")
        return comp

    def add_component(
        self,
        composition_id: str,
        name: str,
        component_type: ComponentType,
        resource_id: str,
        description: str = "",
        parameters: Optional[Dict[str, Any]] = None,
        sequence_order: int = 0,
        depends_on: Optional[List[str]] = None,
    ) -> ApplicationComponent:
        if composition_id not in self._compositions:
            raise ResourceBindingException(f"Composition '{composition_id}' not found.")

        binding = ComponentBinding(
            resource_type=component_type,
            resource_id=resource_id,
            parameters=parameters or {},
        )
        cmp = ApplicationComponent(
            name=name,
            component_type=component_type,
            description=description,
            binding=binding,
            sequence_order=sequence_order,
            depends_on=depends_on or [],
        )
        self._compositions[composition_id].components.append(cmp)
        self._compositions[composition_id].updated_at = datetime.now(timezone.utc)
        return cmp

    def get_composition(self, composition_id: str) -> ApplicationComposition:
        if composition_id not in self._compositions:
            raise ResourceBindingException(f"Composition '{composition_id}' not found.")
        return self._compositions[composition_id]

    def validate_composition(self, composition_id: str) -> Dict[str, Any]:
        """Validate composition bindings and dependency ordering."""
        comp = self.get_composition(composition_id)
        errors = []
        valid_ids = {c.component_id for c in comp.components}

        for c in comp.components:
            if not c.binding.resource_id:
                errors.append(f"Component '{c.name}' missing resource binding ID.")
            for dep in c.depends_on:
                if dep not in valid_ids:
                    errors.append(f"Component '{c.name}' references invalid dependency component '{dep}'.")

        return {
            "composition_id": composition_id,
            "valid": len(errors) == 0,
            "component_count": len(comp.components),
            "errors": errors,
        }
