from .auth import AuthManager
from .exceptions import APIError

class InferenceClient:
    def __init__(self, api_key: str = None, base_url: str = "http://localhost:8000"):
        self.auth = AuthManager(api_key)
        self.base_url = base_url
    
    def chat(self, messages):
        pass
