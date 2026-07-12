from __future__ import annotations

import time
from typing import Any

from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.response import ChatCompletionChoiceMessage, ChatCompletionResponse, Choice, Usage as OpenAIUsage


class OpenAIResponseAdapter:
    """Transforms a standardized inference response into an OpenAI-compatible payload."""

    @staticmethod
    def to_chat_completion_response(response: InferenceResponse, *, request_id: str | None = None) -> ChatCompletionResponse:
        """Convert a standardized response into the OpenAI-compatible chat completion schema."""
        return ChatCompletionResponse(
            id=response.id or f"chatcmpl-{int(time.time())}",
            object="chat.completion",
            created=int(response.created.timestamp()),
            model=response.model,
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionChoiceMessage(role="assistant", content=response.text),
                    finish_reason=response.finish_reason,
                )
            ],
            usage=OpenAIUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
            ),
        )
