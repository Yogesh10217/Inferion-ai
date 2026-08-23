"""Domain Exceptions for Enterprise AI Decision Intelligence Platform (Phase 5.29)."""


class DecisionIntelligenceException(Exception):
    """Base exception for all Decision Intelligence platform errors."""

    def __init__(self, message: str, code: str = "DECISION_INTELLIGENCE_ERROR"):
        super().__init__(message)
        self.message = message
        self.code = code


class DecisionNotFoundException(DecisionIntelligenceException):
    def __init__(self, decision_id: str, tenant_id: str):
        super().__init__(
            f"Decision '{decision_id}' not found for tenant '{tenant_id}'.",
            code="DECISION_NOT_FOUND",
        )


class DecisionContextException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_CONTEXT_ERROR")


class DecisionEvidenceException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_EVIDENCE_ERROR")


class DecisionConstraintViolationException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_CONSTRAINT_VIOLATION")


class DecisionScenarioException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_SCENARIO_ERROR")


class DecisionSimulationException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_SIMULATION_ERROR")


class DecisionRecommendationException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_RECOMMENDATION_ERROR")


class DecisionPolicyViolationException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_POLICY_VIOLATION")


class DecisionRiskException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_RISK_EXCEEDED")


class DecisionApprovalRequiredException(DecisionIntelligenceException):
    def __init__(self, decision_id: str, reason: str):
        super().__init__(
            f"Decision '{decision_id}' requires explicit human approval: {reason}",
            code="DECISION_APPROVAL_REQUIRED",
        )


class ImmutableDecisionException(DecisionIntelligenceException):
    def __init__(self, decision_id: str):
        super().__init__(
            f"Decision '{decision_id}' is finalized and immutable. Further mutations are forbidden.",
            code="IMMUTABLE_DECISION_ERROR",
        )


class DecisionOutcomeException(DecisionIntelligenceException):
    def __init__(self, message: str):
        super().__init__(message, code="DECISION_OUTCOME_ERROR")


class CrossTenantDecisionAccessException(DecisionIntelligenceException):
    def __init__(self, requested_tenant: str, owner_tenant: str):
        super().__init__(
            f"Access denied: Resource belongs to tenant '{owner_tenant}', requested by '{requested_tenant}'. Zero metadata leaked.",
            code="CROSS_TENANT_DECISION_ACCESS_DENIED",
        )
