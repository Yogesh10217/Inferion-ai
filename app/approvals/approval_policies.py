"""
Approval Risk Levels & Policy Definitions
"""

from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ApprovalPolicy:
    """Evaluates whether an action requires human approval based on risk level."""

    @staticmethod
    def requires_approval(action_type: str, risk_level: RiskLevel) -> bool:
        high_risk_actions = {"shell_execution", "database_write", "email_send", "external_payment", "prod_deploy"}
        if action_type in high_risk_actions:
            return True
        return risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL)
