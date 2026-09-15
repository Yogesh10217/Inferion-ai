"""
Mistral Provider implementation.
"""

from typing import Any, AsyncIterator
import uuid

import httpx

from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import InferenceRequest


class MistralProvider(BaseProvider):
    """Provider for Mistral API (mistral-large, mistral-small, codestral)."""

    name = "mistral"

    def __init__(self, api_key: str = "mock-mistral-key", base_url: str = "https://api.mistral.ai/v1"):
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
        model_id = model or (request.model if request else "mistral-large-latest")
        prompt_text = prompt or (self._extract_prompt(request) if request else "Hello")

        if "mock" in self.api_key:
            return InferenceResponse(
                id=f"mistral_{uuid.uuid4().hex[:12]}",
                provider="mistral",
                model=model_id,
                text=f"Response from Mistral {model_id} for: {prompt_text[:30]}",
                finish_reason="stop",
                usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt_text}],
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            content_text = data["choices"][0]["message"]["content"]
            usage_data = data.get("usage", {})
            return InferenceResponse(
                id=data.get("id", f"mistral_{uuid.uuid4().hex[:12]}"),
                provider="mistral",
                model=model_id,
                text=content_text,
                finish_reason="stop",
                usage=Usage(
                    prompt_tokens=usage_data.get("prompt_tokens", 10),
                    completion_tokens=usage_data.get("completion_tokens", 20),
                    total_tokens=usage_data.get("total_tokens", 30),
                ),
            )

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        model_id = model or (request.model if request else "mistral-large-latest")
        yield InferenceResponse(
            id=f"mistral_{uuid.uuid4().hex[:12]}",
            provider="mistral",
            model=model_id,
            text="Mistral streaming chunk.",
            finish_reason="stop",
            usage=Usage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    async def health_check(self) -> bool:
        return True

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="mistral-large-latest", provider="mistral", description="Mistral Large", context_window=128000),
            ProviderModel(id="mistral-small-latest", provider="mistral", description="Mistral Small", context_window=32000),
            ProviderModel(id="codestral-latest", provider="mistral", description="Codestral Code Generation", context_window=32000),
        ]
