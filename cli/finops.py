"""CLI helper for FinOps platform."""

from sdk.python.llm_engine.finops import FinOpsClient


def get_finops_client(base_url: str = "http://localhost:8000") -> FinOpsClient:
    return FinOpsClient(base_url=base_url)
