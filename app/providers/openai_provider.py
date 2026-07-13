from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import ChatMessage, InferenceRequest


class OpenAIProvider(BaseProvider):
    """OpenAI-compatible provider implementation."""

    name = "openai"

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key
        self.base_url = base_url or "https://api.openai.com/v1"

    async def generate(self, *, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> InferenceResponse:
        """Return a standardized response for the prompt."""
        request_obj = request or InferenceRequest(model=model or "", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or ""
        prompt_text = prompt or self._extract_prompt(request_obj)
        created_at = datetime.now(timezone.utc)
        return InferenceResponse(
            id=f"chatcmpl-{model_name}",
            provider=self.name,
            model=model_name,
            text=f"[openai:{model_name}] {prompt_text}",
            usage=Usage(prompt_tokens=max(1, len(prompt_text.split())), completion_tokens=max(1, len(prompt_text.split())), total_tokens=max(1, len(prompt_text.split())) * 2),
            finish_reason="stop",
            latency_ms=0.0,
            created=created_at,
            metadata={"base_url": self.base_url, "provider_version": "v1", "cached": False, **kwargs},
            request_id=kwargs.get("request_id"),
            raw_response=None,
        )

    async def stream(self, *, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> AsyncIterator[str]:
        """Yield OpenAI-style streamed chunks for the completion."""
        request_obj = request or InferenceRequest(model=model or "", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or ""
        prompt_text = prompt or self._extract_prompt(request_obj)
        text = f"[openai:{model_name}] {prompt_text}"
        words = text.split()
        for index, word in enumerate(words):
            chunk = {
                "id": f"chatcmpl-{model_name}",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": model_name,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": word + (" " if index < len(words) - 1 else "")},
                        "finish_reason": None,
                    }
                ],
            }
            yield f"data: {chunk!s}\n\n"
            await asyncio.sleep(0)  # pragma: no cover - pacing hook
        yield "data: [DONE]\n\n"

    async def health_check(self) -> bool:
        """Return True until a real network validation is implemented."""
        return True



    async def list_models(self) -> list[ProviderModel]:
        """Return a small set of example OpenAI-style model metadata."""
        return [
            ProviderModel(
                id="gpt-4o-mini",
                provider=self.name,
                description="OpenAI GPT-4o mini",
                context_window=128000,
                status="available",
            ),
            ProviderModel(
                id="gpt-4.1",
                provider=self.name,
                description="OpenAI GPT-4.1",
                context_window=128000,
                status="available",
            ),
        ]
