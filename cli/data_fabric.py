"""CLI helper for Data Fabric platform."""

from sdk.python.llm_engine.data_fabric import DataFabricClient


def get_data_fabric_client(base_url: str = "http://localhost:8000") -> DataFabricClient:
    return DataFabricClient(base_url=base_url)
