"""CLI helper for MLOps platform."""

from sdk.python.llm_engine.mlops import MLOpsClient


def get_mlops_client(base_url: str = "http://localhost:8000") -> MLOpsClient:
    return MLOpsClient(base_url=base_url)
