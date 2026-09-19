"""Runtime Blast Radius Analyzer for Phase 5.57 Runtime Intelligence."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

logger = logging.getLogger(__name__)


@dataclass
class RuntimeBlastRadiusAssessment:
    assessment_id: str
    tenant_id: str
    target_resource_id: str
    affected_services: List[str]
    affected_dependencies: List[str]
    affected_tenants_count: int
    blast_radius_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    estimated_recovery_complexity: str  # SIMPLE, MODERATE, COMPLEX, SEVERE
    assessed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeBlastRadiusAnalyzer:
    """Evaluates blast radius and cascading failure potential across runtime dependencies."""

    def evaluate_blast_radius(
        self, tenant_id: str, target_resource_id: str, downstream_deps: List[str]
    ) -> RuntimeBlastRadiusAssessment:
        level = (
            "CRITICAL"
            if len(downstream_deps) >= 5
            else ("HIGH" if len(downstream_deps) >= 3 else "MEDIUM" if len(downstream_deps) >= 1 else "LOW")
        )
        complexity = "COMPLEX" if len(downstream_deps) >= 3 else "MODERATE"

        ass = RuntimeBlastRadiusAssessment(
            assessment_id=f"blast_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            affected_services=[target_resource_id],
            affected_dependencies=downstream_deps,
            affected_tenants_count=1,
            blast_radius_level=level,
            estimated_recovery_complexity=complexity,
        )
        logger.info(
            f"Evaluated blast radius for '{target_resource_id}': level={level}, downstream={len(downstream_deps)}"
        )
        return ass
