"""CLI helper for extensions framework."""

from sdk.python.llm_engine.extensions import ExtensionsClient


def get_extensions_client(base_url: str = "http://localhost:8000") -> ExtensionsClient:
    return ExtensionsClient(base_url=base_url)
