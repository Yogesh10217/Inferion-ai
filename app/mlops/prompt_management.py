"""PromptOps & Immutable Prompt Versioning Platform."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.mlops.registry import AIAssetRegistry, AIAssetType, AIAssetStatus, AIAssetVersion

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PromptTemplate(BaseModel):
    template_str: str
    input_variables: List[str] = Field(default_factory=list)


class PromptEvaluationScore(BaseModel):
    quality_score: float = 90.0
    hallucination_score: float = 0.02
    latency_ms: float = 85.0
    cost_dollars: float = 0.0005


class PromptManager:
    """PromptOps Platform managing immutable prompt templates, variable substitution, and evaluation tracking."""

    def __init__(self, registry: Optional[AIAssetRegistry] = None) -> None:
        self.registry = registry or AIAssetRegistry()

    def create_prompt(
        self,
        name: str,
        template_str: str,
        input_variables: Optional[List[str]] = None,
        tenant_id: str = "global",
        description: str = "",
    ) -> str:
        config = {
            "template_str": template_str,
            "input_variables": input_variables or [],
            "evaluation": PromptEvaluationScore().model_dump(),
        }
        asset = self.registry.register_asset(
            name=name,
            asset_type=AIAssetType.PROMPT_TEMPLATE,
            tenant_id=tenant_id,
            description=description,
            initial_configuration=config,
        )
        logger.info(f"[PROMPTOPS] Created prompt '{name}' (Asset ID: {asset.asset_id})")
        return asset.asset_id

    def create_version(
        self,
        prompt_asset_id: str,
        version_number: str,
        template_str: str,
        input_variables: Optional[List[str]] = None,
        changelog: str = "",
    ) -> AIAssetVersion:
        config = {
            "template_str": template_str,
            "input_variables": input_variables or [],
            "evaluation": PromptEvaluationScore().model_dump(),
        }
        ver = self.registry.create_version(
            asset_id=prompt_asset_id,
            version_number=version_number,
            configuration=config,
            changelog=changelog,
        )
        logger.info(f"[PROMPTOPS] Created prompt version '{version_number}' for asset '{prompt_asset_id}'")
        return ver

    def render_template(self, prompt_asset_id: str, version_number: str, variables: Dict[str, Any]) -> str:
        ver = self.registry.get_version(prompt_asset_id, version_number)
        template_str = ver.configuration.get("template_str", "")

        rendered = template_str
        for k, v in variables.items():
            rendered = rendered.replace(f"{{{k}}}", str(v))

        return rendered

    def promote_prompt(self, prompt_asset_id: str, version_number: str, target_status: AIAssetStatus = AIAssetStatus.PRODUCTION) -> AIAssetVersion:
        return self.registry.promote_version(prompt_asset_id, version_number, target_status)
