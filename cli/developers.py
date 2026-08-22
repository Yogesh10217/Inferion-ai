"""CLI helper for developers platform."""

from sdk.python.llm_engine.developers import DevelopersClient


def get_developers_client(base_url: str = "http://localhost:8000") -> DevelopersClient:
    return DevelopersClient(base_url=base_url)
