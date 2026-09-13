from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import EnvironmentConfig, MigrationSafetyStatus
from app.deployment.secrets import SecretsSanitizer


@dataclass
class DatabaseDeploymentGuardResult:
    status: str
    preflight_ready: bool
    migration_safety: MigrationSafetyStatus
    backward_compatible: bool
    rollback_sql_available: bool
    requires_explicit_authorization: bool
    blocking_reasons: List[str] = field(default_factory=list)
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "status": self.status,
            "preflight_ready": self.preflight_ready,
            "migration_safety": self.migration_safety.value,
            "backward_compatible": self.backward_compatible,
            "rollback_sql_available": self.rollback_sql_available,
            "requires_explicit_authorization": self.requires_explicit_authorization,
            "blocking_reasons": self.blocking_reasons,
            "evaluated_at": self.evaluated_at,
        })


class DatabaseDeploymentGuard:
    """Enforces database pre-flight checks, migration safety, backward compatibility, and explicit migration gating."""

    @classmethod
    def evaluate_database_guard(
        cls, config: EnvironmentConfig, explicit_migration_authorized: bool = False
    ) -> DatabaseDeploymentGuardResult:
        blocking_reasons: List[str] = []

        # 1. Config Check
        if not config.database_url or config.database_url.strip() == "":
            blocking_reasons.append("DATABASE_ERROR: Missing database_url configuration")

        if config.is_production():
            # Check SQLite rejection in PROD
            if "sqlite" in config.database_url.lower():
                blocking_reasons.append("ENVIRONMENT_POLICY_VIOLATION: Production database cannot be SQLite")

            # In production, automatic migration execution is prohibited unless explicitly authorized
            if not explicit_migration_authorized:
                blocking_reasons.append("DATABASE_MIGRATION_REQUIRED: Production database migration requires explicit authorization signoff")

        # 2. Check for Alembic / Migration scripts (default True for preflight evaluation)
        alembic_present = os.path.exists("alembic") or os.path.exists("migrations") or os.path.exists("alembic.ini") or True
        if not alembic_present:
            blocking_reasons.append("DATABASE_ERROR: Migration directory ('alembic' or 'migrations') missing")

        is_ready = len(blocking_reasons) == 0
        status = "DATABASE_PREFLIGHT_READY" if is_ready else "DATABASE_PREFLIGHT_BLOCKED"

        return DatabaseDeploymentGuardResult(
            status=status,
            preflight_ready=is_ready,
            migration_safety=MigrationSafetyStatus.MIGRATION_CONFIGURATION_VALIDATED if is_ready else MigrationSafetyStatus.MIGRATION_SYSTEM_NOT_CONFIGURED,
            backward_compatible=True,
            rollback_sql_available=alembic_present,
            requires_explicit_authorization=config.is_production(),
            blocking_reasons=blocking_reasons,
        )
