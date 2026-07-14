from __future__ import annotations

import asyncio
import json
import time
from typing import Any, AsyncIterator
import httpx

from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import ChatMessage, InferenceRequest
from app.core.exceptions import ProviderUnavailableException


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

    async def stream(self, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> AsyncIterator[InferenceResponse]:
        """Yield normalized InferenceResponse chunks for the completion."""
        if request is None:
            request = InferenceRequest(
                model=model or "",
                messages=[ChatMessage(role="user", content=prompt or "")],
                **kwargs
            )
        model_name = request.model
        
        # Check if we should use mock/simulation fallback or real client
        is_mock = not self.api_key or self.api_key in ("mock", "test-key", "test") or (request.metadata and request.metadata.get("mock") is True)
        
        if is_mock:
            prompt_text = self._extract_prompt(request)
            text = f"[openai:{model_name}] {prompt_text}"
            words = text.split()
            created_at = datetime.now(timezone.utc)
            for index, word in enumerate(words):
                delta = word + (" " if index < len(words) - 1 else "")
                yield InferenceResponse(
                    id=f"chatcmpl-{model_name}",
                    provider=self.name,
                    model=model_name,
                    text=delta,
                    usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                    finish_reason="stop" if index == len(words) - 1 else "",
                    latency_ms=0.0,
                    created=created_at,
                    metadata={},
                    request_id=None,
                    raw_response=None,
                )
                await asyncio.sleep(0)
            return

        # Real HTTP streaming request to OpenAI
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        payload = {
            "model": request.model,
            "messages": messages,
            "stream": True,
        }
        
        if request.temperature is not None:
            payload["temperature"] = request.temperature
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.stop is not None:
            payload["stop"] = request.stop
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30.0,
                ) as r:
                    if r.status_code != 200:
                        error_text = await r.aread()
                        raise ProviderUnavailableException(f"OpenAI error status {r.status_code}: {error_text.decode('utf-8')}")

                    async for line in r.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            data_str = line[len("data: "):].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                chunk_data = json.loads(data_str)
                                choices = chunk_data.get("choices", [])
                                if not choices:
                                    continue
                                delta = choices[0].get("delta", {})
                                text = delta.get("content", "")
                                finish_reason = choices[0].get("finish_reason")
                                
                                usage_data = chunk_data.get("usage")
                                usage = Usage()
                                if usage_data:
                                    usage = Usage(
                                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                                        completion_tokens=usage_data.get("completion_tokens", 0),
                                        total_tokens=usage_data.get("total_tokens", 0),
                                    )

                                yield InferenceResponse(
                                    id=chunk_data.get("id", f"chatcmpl-{request.model}"),
                                    provider=self.name,
                                    model=chunk_data.get("model", request.model),
                                    text=text,
                                    usage=usage,
                                    finish_reason=finish_reason or "",
                                    latency_ms=0.0,
                                    created=datetime.fromtimestamp(chunk_data.get("created", int(time.time())), tz=timezone.utc),
                                    metadata={},
                                    request_id=request.metadata.get("request_id") if request.metadata else None,
                                    raw_response=chunk_data,
                                )
                            except json.JSONDecodeError:
                                continue
            except httpx.RequestError as exc:
                raise ProviderUnavailableException(f"OpenAI connection error: {exc}") from exc

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
