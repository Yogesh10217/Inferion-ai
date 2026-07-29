from typing import Dict

class AuthProvider:
    def get_headers(self) -> Dict[str, str]:
        return {}

class APIKeyAuth(AuthProvider):
    def __init__(self, api_key: str, header_name: str = "X-API-Key"):
        self.api_key = api_key
        self.header_name = header_name

    def get_headers(self) -> Dict[str, str]:
        return {self.header_name: self.api_key}

class BearerAuth(AuthProvider):
    def __init__(self, token: str):
        self.token = token

    def get_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token}"}
