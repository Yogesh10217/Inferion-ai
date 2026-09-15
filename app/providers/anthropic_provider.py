"""
Anthropic Claude Provider implementation.
"""

from typing import Any, AsyncIterator
import uuid

import httpx

from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import InferenceRequest


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude API (claude-3-5-sonnet, claude-3-haiku, etc.)."""

    name = "anthropic"

    def __init__(self, api_key: str = "mock-anthropic-key", base_url: str = "https://api.anthropic.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    async def generate(
        self,
        *,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> InferenceResponse:
        model_id = model or (request.model if request else "claude-3-5-sonnet")
        prompt_text = prompt or (self._extract_prompt(request) if request else "Hello")

        if "mock" in self.api_key:
            return InferenceResponse(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                provider="anthropic",
                model=model_id,
                text=f"Response from Anthropic {model_id} for: {prompt_text[:30]}",
                finish_reason="stop",
                usage=Usage(prompt_tokens=15, completion_tokens=25, total_tokens=40),
            )

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload = {
            "model": model_id,
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt_text}],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/messages", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content_text = data["content"][0]["text"] if data.get("content") else ""
            usage_data = data.get("usage", {})
            return InferenceResponse(
                id=data.get("id", f"msg_{uuid.uuid4().hex[:12]}"),
                provider="anthropic",
                model=model_id,
                text=content_text,
                finish_reason="stop",
                usage=Usage(
                    prompt_tokens=usage_data.get("input_tokens", 10),
                    completion_tokens=usage_data.get("output_tokens", 20),
                    total_tokens=usage_data.get("input_tokens", 10) + usage_data.get("output_tokens", 20),
                ),
            )

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        model_id = model or (request.model if request else "claude-3-5-sonnet")
        yield InferenceResponse(
            id=f"msg_{uuid.uuid4().hex[:12]}",
            provider="anthropic",
            model=model_id,
            text="Anthropic streaming response chunk.",
            finish_reason="stop",
            usage=Usage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    async def health_check(self) -> bool:
        return True

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="claude-3-5-sonnet", provider="anthropic", description="Anthropic Claude 3.5 Sonnet", context_window=200000),
            ProviderModel(id="claude-3-haiku", provider="anthropic", description="Anthropic Claude 3 Haiku", context_window=200000),
            ProviderModel(id="claude-3-opus", provider="anthropic", description="Anthropic Claude 3 Opus", context_window=200000),
        ]
