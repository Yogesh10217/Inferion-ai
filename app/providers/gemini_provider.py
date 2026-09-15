"""
Google Gemini Provider implementation.
"""

from typing import Any, AsyncIterator
import uuid

import httpx

from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import InferenceRequest


class GeminiProvider(BaseProvider):
    """Provider for Google Gemini API (gemini-1.5-pro, gemini-1.5-flash)."""

    name = "gemini"

    def __init__(self, api_key: str = "mock-gemini-key", base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
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
        model_id = model or (request.model if request else "gemini-1.5-pro")
        prompt_text = prompt or (self._extract_prompt(request) if request else "Hello")

        if "mock" in self.api_key:
            return InferenceResponse(
                id=f"gemini_{uuid.uuid4().hex[:12]}",
                provider="gemini",
                model=model_id,
                text=f"Response from Gemini {model_id} for: {prompt_text[:30]}",
                finish_reason="stop",
                usage=Usage(prompt_tokens=12, completion_tokens=22, total_tokens=34),
            )

        endpoint = f"{self.base_url}/models/{model_id}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(endpoint, json=payload)
            resp.raise_for_status()
            data = resp.json()
            content_text = ""
            if data.get("candidates"):
                content_text = data["candidates"][0]["content"]["parts"][0]["text"]

            return InferenceResponse(
                id=f"gemini_{uuid.uuid4().hex[:12]}",
                provider="gemini",
                model=model_id,
                text=content_text,
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
        model_id = model or (request.model if request else "gemini-1.5-pro")
        yield InferenceResponse(
            id=f"gemini_{uuid.uuid4().hex[:12]}",
            provider="gemini",
            model=model_id,
            text="Gemini streaming chunk.",
            finish_reason="stop",
            usage=Usage(prompt_tokens=10, completion_tokens=10, total_tokens=20),
        )

    async def health_check(self) -> bool:
        return True

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="gemini-1.5-pro", provider="gemini", description="Google Gemini 1.5 Pro", context_window=1000000),
            ProviderModel(id="gemini-1.5-flash", provider="gemini", description="Google Gemini 1.5 Flash", context_window=1000000),
        ]
