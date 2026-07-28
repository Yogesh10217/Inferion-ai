from fastapi import HTTPException, status

class RateLimitExceededException(HTTPException):
    def __init__(self, detail: str = "Rate limit exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)

class QuotaExceededException(HTTPException):
    def __init__(self, detail: str = "Quota exceeded"):
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail)
