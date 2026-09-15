"""
Cohere Provider implementation.
"""

from typing import Any, AsyncIterator
import uuid

import httpx

from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import InferenceRequest


class CohereProvider(BaseProvider):
    """Provider for Cohere API (command-r-plus, command-r)."""

    name = "cohere"

    def __init__(self, api_key: str = "mock-cohere-key", base_url: str = "https://api.cohere.com/v1"):
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
        model_id = model or (request.model if request else "command-r-plus")
        prompt_text = prompt or (self._extract_prompt(request) if request else "Hello")

        if "mock" in self.api_key:
            return InferenceResponse(
                id=f"cohere_{uuid.uuid4().hex[:12]}",
                provider="cohere",
                model=model_id,
                text=f"Response from Cohere {model_id} for: {prompt_text[:30]}",
                finish_reason="stop",
                usage=Usage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            )

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {"model": model_id, "message": prompt_text}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(f"{self.base_url}/chat", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return InferenceResponse(
                id=data.get("response_id", f"cohere_{uuid.uuid4().hex[:12]}"),
                provider="cohere",
                model=model_id,
                text=data.get("text", ""),
                finish_reason="stop",
                usage=Usage(prompt_tokens=15, completion_tokens=25, total_tokens=40),
            )

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        model_id = model or (request.model if request else "command-r-plus")
        yield InferenceResponse(
            id=f"cohere_{uuid.uuid4().hex[:12]}",
            provider="cohere",
            model=model_id,
            text="Cohere streaming chunk.",
            finish_reason="stop",
            usage=Usage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    async def health_check(self) -> bool:
        return True

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="command-r-plus", provider="cohere", description="Cohere Command R+", context_window=128000),
            ProviderModel(id="command-r", provider="cohere", description="Cohere Command R", context_window=128000),
        ]
