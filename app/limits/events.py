from abc import ABC, abstractmethod
from typing import Optional


class UsageEvent:
    def __init__(
        self,
        organization_id: str,
        provider: str,
        model: str,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        api_key_id: Optional[str] = None,
        request_tokens: int = 0,
        response_tokens: int = 0,
        status_code: Optional[str] = None,
        error_type: Optional[str] = None,
        is_streaming: bool = False,
        is_cached: bool = False,
        duration_ms: int = 0,
    ):
        self.organization_id = organization_id
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.api_key_id = api_key_id
        self.provider = provider
        self.model = model
        self.request_tokens = request_tokens
        self.response_tokens = response_tokens
        self.total_tokens = request_tokens + response_tokens
        self.status_code = status_code
        self.error_type = error_type
        self.is_streaming = is_streaming
        self.is_cached = is_cached
        self.duration_ms = duration_ms


class UsageEventEmitter(ABC):
    """Abstract interface for emitting usage events asynchronously."""

    @abstractmethod
    def emit(self, event: UsageEvent) -> None:
        """Emit a usage event without blocking the execution path."""
