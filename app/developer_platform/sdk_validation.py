"""Developer SDK Consistency Validator across Python, TypeScript, Go, and Java."""

import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SDKContractReport(BaseModel):
    """Validation report tracking multi-language SDK API coverage."""

    sdk_language: str
    total_endpoints: int
    covered_endpoints: int
    missing_endpoints: List[str] = Field(default_factory=list)
    schema_mismatches: List[str] = Field(default_factory=list)
    is_compliant: bool = True


class SDKConsistencyValidator:
    """Validates API coverage and schema contract consistency across Python, TypeScript, Go, and Java SDKs."""

    REQUIRED_ENDPOINTS = [
        "/v1/developers/projects",
        "/v1/extensions",
        "/v1/extensions/{id}/install",
        "/v1/extensions/{id}/enable",
        "/v1/extensions/{id}/disable",
        "/v1/extensions/{id}/upgrade",
        "/v1/extensions/{id}/rollback",
        "/v1/marketplace/items",
        "/v1/marketplace/items/{id}/submit",
        "/v1/marketplace/items/{id}/approve",
        "/v1/marketplace/items/{id}/publish",
        "/v1/marketplace/items/{id}/install",
        "/v1/events/subscriptions",
    ]

    def validate_sdk_contract(self, language: str, implemented_methods: List[str]) -> SDKContractReport:
        """Validate an SDK implementation against canonical platform API contract."""
        missing = []
        for req_ep in self.REQUIRED_ENDPOINTS:
            # Simple contract check matching endpoint keyword
            key = req_ep.split("/")[-1].replace("{id}", "")
            if not any(key in m.lower() for m in implemented_methods):
                missing.append(req_ep)

        is_compliant = len(missing) == 0
        logger.info(f"[SDK VALIDATOR] Validated {language} SDK: {len(self.REQUIRED_ENDPOINTS) - len(missing)}/{len(self.REQUIRED_ENDPOINTS)} endpoints covered")

        return SDKContractReport(
            sdk_language=language,
            total_endpoints=len(self.REQUIRED_ENDPOINTS),
            covered_endpoints=len(self.REQUIRED_ENDPOINTS) - len(missing),
            missing_endpoints=missing,
            is_compliant=is_compliant,
        )
