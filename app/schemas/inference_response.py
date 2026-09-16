from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class Usage(BaseModel):
    """Token usage statistics for a standardized inference response."""

    model_config = ConfigDict(extra="forbid")

    prompt_tokens: int = Field(default=0, ge=0, description="Number of prompt tokens.")
    completion_tokens: int = Field(default=0, ge=0, description="Number of completion tokens.")
    total_tokens: int = Field(default=0, ge=0, description="Total tokens used.")


class InferenceResponse(BaseModel):
    """Normalized success response emitted by providers.

    This object is the single response contract used across providers and the
    inference service. It keeps provider-specific SDK payloads inside the provider
    layer and allows the adapter layer to translate it to API-specific formats.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Unique identifier for the inference response.")
    provider: str = Field(..., description="Provider that produced the response.")
    model: str = Field(..., description="Model identifier used for inference.")
    text: str = Field(..., description="The generated text content.")
    usage: Usage = Field(default_factory=Usage, description="Token usage statistics.")
    finish_reason: str = Field(default="stop", description="Reason generation stopped.")
    latency_ms: float = Field(default=0.0, ge=0.0, description="Provider latency in milliseconds.")
    created: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Timestamp of response creation.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Provider-agnostic metadata.")
    request_id: str | None = Field(default=None, description="Optional request correlation identifier.")
    raw_response: Any | None = Field(default=None, description="Provider-specific raw payload, if any.")
