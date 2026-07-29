class SDKError(Exception):
    pass

class AuthenticationError(SDKError):
    pass

class RateLimitError(SDKError):
    pass

class TimeoutError(SDKError):
    pass

class APIError(SDKError):
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details or {}
