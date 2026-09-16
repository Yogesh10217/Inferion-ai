from fastapi import HTTPException, status


class BillingException(HTTPException):
    pass


class BudgetExceededException(BillingException):
    def __init__(self, detail: str = "Hard budget limit exceeded"):
        super().__init__(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)


class SubscriptionExpiredException(BillingException):
    def __init__(self, detail: str = "Subscription has expired"):
        super().__init__(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=detail)


class InvalidPlanException(BillingException):
    def __init__(self, detail: str = "Invalid subscription plan"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
