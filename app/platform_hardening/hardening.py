"""
Platform Hardening Engine.
Prioritizes findings (P0, P1, P2, P3), groups root patterns, and manages platform hardening workflows.
"""

from typing import Dict, List

from app.platform_hardening.models import (
    PlatformAuditFinding,
    RemediationRecommendation,
)
from app.platform_hardening.remediation import PlatformRemediationPlanner


class PlatformHardeningEngine:
    """Coordinates finding prioritization, root pattern analysis, and hardening remediation plans."""

    def __init__(self):
        self.planner = PlatformRemediationPlanner()

    def create_hardening_plan(
        self, findings: List[PlatformAuditFinding], tenant_id: str = "system"
    ) -> Dict[str, List[RemediationRecommendation]]:
        all_remediations = self.planner.generate_remediations(findings, tenant_id=tenant_id)

        grouped: Dict[str, List[RemediationRecommendation]] = {
            "P0": [],
            "P1": [],
            "P2": [],
            "P3": [],
        }

        for rem in all_remediations:
            prio = rem.priority if rem.priority in grouped else "P3"
            grouped[prio].append(rem)

        return grouped
