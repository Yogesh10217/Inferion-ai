class ProviderSelector:
    def select(self, ranked_providers: list[tuple[str, float]]) -> str:
        if not ranked_providers:
            return None
        return ranked_providers[0][0]
