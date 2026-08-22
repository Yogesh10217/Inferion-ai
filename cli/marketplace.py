"""CLI helper for marketplace platform."""

from sdk.python.llm_engine.marketplace import MarketplaceClient


def get_marketplace_client(base_url: str = "http://localhost:8000") -> MarketplaceClient:
    return MarketplaceClient(base_url=base_url)
