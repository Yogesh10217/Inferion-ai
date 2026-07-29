class APIError(Exception): pass
class AuthenticationException(APIError): pass
class RateLimitException(APIError): pass
