"""Control Plane Configuration Validator ensuring safety and compliance."""

import logging
from typing import Dict, Any, List
from app.control_plane.exceptions import ConfigurationException, PolicyViolationException

logger = logging.getLogger(__name__)


class ControlPlaneConfigurationValidator:
    """Validates configuration changes against security rules, resource constraints, and production policies."""

    @staticmethod
    def validate_configuration(settings: Dict[str, Any], environment: str = "production") -> Dict[str, Any]:
        """Validate proposed configuration dictionary."""
        errors: List[str] = []
        warnings: List[str] = []

        # 1. Unsafe security settings
        if settings.get("allow_insecure_http") is True and environment == "production":
            errors.append("Unsafe policy: 'allow_insecure_http' is set to True in production environment")

        if settings.get("bypass_auth") is True:
            errors.append("Security violation: 'bypass_auth' is enabled")

        # 2. Resource limit checks
        if "max_concurrent_agents" in settings and settings["max_concurrent_agents"] < 1:
            errors.append("Invalid limit: 'max_concurrent_agents' must be >= 1")

        if "max_tokens_per_month" in settings and settings["max_tokens_per_month"] <= 0:
            errors.append("Invalid limit: 'max_tokens_per_month' must be positive")

        if errors:
            err_msg = "; ".join(errors)
            logger.error(f"[CONFIG VALIDATOR FAILED] {err_msg}")
            raise PolicyViolationException(err_msg, details={"errors": errors})

        return {
            "valid": True,
            "environment": environment,
            "errors": errors,
            "warnings": warnings,
        }
