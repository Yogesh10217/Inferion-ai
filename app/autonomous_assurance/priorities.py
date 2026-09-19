"""
Workflow Priority Engine Subsystem.
Calculates dynamic workflow priority based on security severity, business impact, operational impact, risk, and SLA urgency.
"""

from app.autonomous_assurance.workflows import WorkflowPriority


class WorkflowPriorityEngine:
    """Evaluates dynamic priority scores for workflows."""

    def calculate_priority(
        self,
        security_severity: str = "MEDIUM",
        business_impact: str = "MEDIUM",
        ops_impact: str = "MEDIUM",
        risk_score: float = 20.0,
        urgency: str = "NORMAL",
        impact_score: float = 0.0,
        urgency_score: float = 0.0,
    ) -> WorkflowPriority:
        eff_risk = max(risk_score, (impact_score + urgency_score) / 2.0)
        if (
            security_severity in ("CRITICAL", "EMERGENCY")
            or urgency == "EMERGENCY"
            or eff_risk >= 80.0
            or impact_score >= 80.0
        ):
            return WorkflowPriority.CRITICAL
        elif security_severity == "HIGH" or business_impact == "HIGH" or eff_risk >= 50.0:
            return WorkflowPriority.HIGH
        elif security_severity == "MEDIUM" or ops_impact == "MEDIUM":
            return WorkflowPriority.HIGH
        elif security_severity == "LOW":
            return WorkflowPriority.MEDIUM
        return WorkflowPriority.LOW
