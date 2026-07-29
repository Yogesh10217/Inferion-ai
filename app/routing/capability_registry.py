class CapabilityRegistry:
    def __init__(self):
        self.capabilities = {}
        
    def register(self, provider_id: str, caps: list[str]):
        self.capabilities[provider_id] = caps
        
    def get_providers_with_capability(self, cap: str) -> list[str]:
        return []
