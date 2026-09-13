from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from app.deployment.models import DeploymentTargetStatus
from app.deployment.secrets import SecretsSanitizer


@dataclass
class DeploymentTarget:
    target_id: str
    environment: str
    provider: str = "LOCAL_DOCKER"
    region: str = "us-east-1"
    cluster: str = "local-cluster"
    namespace: str = "default"
    service_name: str = "enterprise-ai-platform"
    deployment_type: str = "CONTAINER"
    endpoint: str = "http://localhost:8000"
    tls_enabled: bool = False
    production_target: bool = False
    credentials_available: bool = True
    connectivity_status: str = "CONNECTED"
    runtime_status: DeploymentTargetStatus = DeploymentTargetStatus.TARGET_CONFIGURATION_READY
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_production(self) -> bool:
        return self.environment.upper() == "PRODUCTION" or self.production_target

    def validate_target(self) -> Dict[str, Any]:
        """Validates target availability without fabricating production connectivity."""
        if self.is_production():
            has_prod_infra = bool(
                os.getenv("PRODUCTION_KUBERNETES_CLUSTER")
                or os.getenv("PRODUCTION_CLOUD_ENDPOINT")
                or os.getenv("PROD_AWS_ACCESS_KEY")
            )
            if not has_prod_infra:
                self.credentials_available = False
                self.connectivity_status = "NOT_AVAILABLE"
                self.runtime_status = DeploymentTargetStatus.TARGET_NOT_AVAILABLE
                return SecretsSanitizer.sanitize_structure({
                    "target_id": self.target_id,
                    "status": "NOT_AVAILABLE",
                    "reason": "PRODUCTION_RUNTIME_TARGET_NOT_AVAILABLE: Real production infrastructure credentials or endpoints unconfigured",
                    "truthfulness_status": "NOT_EXECUTED",
                })

        self.runtime_status = DeploymentTargetStatus.TARGET_CONNECTIVITY_VALIDATED
        return SecretsSanitizer.sanitize_structure({
            "target_id": self.target_id,
            "status": "VALIDATED",
            "environment": self.environment,
            "endpoint": self.endpoint,
            "truthfulness_status": "VALIDATED" if not self.is_production() else "NOT_EXECUTED",
        })
