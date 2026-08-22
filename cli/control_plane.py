"""CLI helper for control plane management."""

from sdk.python.llm_engine.control_plane import ControlPlaneClient


def get_control_plane_client(base_url: str = "http://localhost:8002") -> ControlPlaneClient:
    return ControlPlaneClient(base_url=base_url)
