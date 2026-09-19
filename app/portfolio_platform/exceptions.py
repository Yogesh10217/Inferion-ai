"""Domain exceptions for Enterprise AI Portfolio, Strategy, Value & Investment Governance Platform."""


class PortfolioException(Exception):
    """Base exception for all portfolio platform errors."""

    def __init__(self, message: str, tenant_id: str = "global", details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.tenant_id = tenant_id
        self.details = details or {}


class PortfolioNotFoundException(PortfolioException):
    def __init__(self, portfolio_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Portfolio '{portfolio_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id)


class InitiativeNotFoundException(PortfolioException):
    def __init__(self, initiative_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"AI Initiative '{initiative_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id)


class BusinessCaseNotFoundException(PortfolioException):
    def __init__(self, business_case_id: str, tenant_id: str = "global") -> None:
        super().__init__(f"Business Case '{business_case_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id)


class InvestmentNotFoundException(PortfolioException):
    def __init__(self, investment_id: str, tenant_id: str = "global") -> None:
        super().__init__(
            f"Investment Proposal/Decision '{investment_id}' not found for tenant '{tenant_id}'.", tenant_id=tenant_id
        )


class FundingDecisionException(PortfolioException):
    pass


class PortfolioOptimizationException(PortfolioException):
    pass


class ValueMeasurementException(PortfolioException):
    pass


class BenefitsRealizationException(PortfolioException):
    pass


class ImmutablePortfolioSnapshotException(PortfolioException):
    def __init__(self, snapshot_id: str, tenant_id: str = "global") -> None:
        super().__init__(
            f"Immutability Violation: Finalized portfolio snapshot '{snapshot_id}' cannot be modified.",
            tenant_id=tenant_id,
        )


class ImmutableInvestmentDecisionException(PortfolioException):
    def __init__(self, decision_id: str, tenant_id: str = "global") -> None:
        super().__init__(
            f"Immutability Violation: Finalized investment decision '{decision_id}' cannot be modified.",
            tenant_id=tenant_id,
        )


class CrossTenantPortfolioAccessException(PortfolioException):
    def __init__(self, request_tenant: str, target_tenant: str, resource_id: str) -> None:
        super().__init__(
            f"Access Denied: Tenant '{request_tenant}' cannot access portfolio resource '{resource_id}' owned by tenant '{target_tenant}'.",
            tenant_id=request_tenant,
        )


class StrategyAlignmentException(PortfolioException):
    pass


class PortfolioPolicyViolationException(PortfolioException):
    pass
