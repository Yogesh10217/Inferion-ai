"""CLI helper for Operations platform."""

from sdk.python.llm_engine.operations import OperationsClient


def get_operations_client(base_url: str = "http://localhost:8000") -> OperationsClient:
    return OperationsClient(base_url=base_url)
