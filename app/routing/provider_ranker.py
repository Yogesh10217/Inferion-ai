class ProviderRanker:
    def rank(self, providers: list[str], policy, metrics, health) -> list[tuple[str, float]]:
        return [(p, 1.0) for p in providers]
