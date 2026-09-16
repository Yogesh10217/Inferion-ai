"""Dependency Intelligence & Vulnerability Blast Radius Subsystem."""

import logging
import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.developer_platform.exceptions import DependencyRiskViolationException

logger = logging.getLogger(__name__)


class DependencyRisk(BaseModel):
    risk_id: str = Field(default_factory=lambda: f"drisk_{uuid.uuid4().hex[:10]}")
    dependency_name: str
    version: str
    risk_level: str = "LOW"
    cve_id: Optional[str] = None
    tenant_id: str = "global"


class DependencyManager:
    """Tracks project dependencies, transitive vulnerabilities, and blast radius risks."""

    def analyze_dependencies(self, dependencies: List[Dict[str, str]], tenant_id: str = "global") -> List[DependencyRisk]:
        risks = []
        for d in dependencies:
            name = d.get("name", "")
            r_level = d.get("risk_level", "LOW")
            risk = DependencyRisk(dependency_name=name, version=d.get("version", "1.0.0"), risk_level=r_level, tenant_id=tenant_id)
            risks.append(risk)

            if r_level in ("HIGH", "CRITICAL"):
                logger.warning(f"[DEPENDENCY INTELLIGENCE] Critical vulnerability detected in dependency '{name}' ({r_level})")
                raise DependencyRiskViolationException(name, r_level)

        logger.info(f"[DEPENDENCY INTELLIGENCE] Analyzed {len(dependencies)} dependencies for tenant '{tenant_id}'")
        return risks
