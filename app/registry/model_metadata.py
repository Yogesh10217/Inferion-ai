from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

ModelStatus = str


@dataclass
class ModelMetadata:
    """Strongly typed model metadata representing a model in the engine."""

    id: str
    provider: str
    display_name: str | None = None
    description: str = ""
    version: str | None = None
    context_window: int | None = None
    max_output_tokens: int | None = None
    supports_streaming: bool = True
    supports_tools: bool = False
    supports_images: bool = False
    supports_embeddings: bool = False
    status: ModelStatus = "available"
    pricing: dict[str, Any] | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc)
        if self.updated_at is None:
            self.updated_at = self.created_at


# Alias for backward compatibility
RegisteredModel = ModelMetadata
