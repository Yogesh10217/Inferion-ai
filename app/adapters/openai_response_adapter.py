from __future__ import annotations

import time
from typing import Any

from app.schemas.inference_response import InferenceResponse
from app.schemas.response import ChatCompletionChoiceMessage, ChatCompletionResponse, Choice
from app.schemas.response import Usage as OpenAIUsage


class OpenAIResponseAdapter:
    """Transforms a standardized inference response into an OpenAI-compatible payload."""

    @staticmethod
    def to_chat_completion_response(
        response: InferenceResponse, *, request_id: str | None = None
    ) -> ChatCompletionResponse:
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

    @staticmethod
    def to_chat_completion_chunk(response: InferenceResponse) -> dict[str, Any]:
        """Convert a standardized response chunk into the OpenAI-compatible chat completion chunk schema."""
        return {
            "id": response.id or f"chatcmpl-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(response.created.timestamp()),
            "model": response.model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": response.text} if response.text else {},
                    "finish_reason": response.finish_reason if response.finish_reason else None,
                }
            ],
            "usage": (
                {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
                if response.usage and (response.usage.prompt_tokens or response.usage.completion_tokens)
                else None
            ),
        }


def format_sse_event(*, data: str = "", event: str | None = None, comment: str | None = None) -> bytes:
    """Format SSE lines into a raw bytes representation.

    Allows heartbeats and other custom events to be injected easily later.
    """
    lines = []
    if comment:
        lines.append(f": {comment}")
    if event:
        lines.append(f"event: {event}")
    if data:
        lines.append(f"data: {data}")
    return ("\n".join(lines) + "\n\n").encode("utf-8")
