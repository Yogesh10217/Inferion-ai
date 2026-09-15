"""
Google Gemini Provider implementation.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import httpx

from app.core.config import get_settings
from app.core.exceptions import ProviderUnavailableException
from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import ChatMessage, InferenceRequest


class GeminiProvider(BaseProvider):
    """Provider for Google Gemini API (gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash)."""

    name = "gemini"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.gemini_api_key
        self.base_url = (base_url or "https://generativelanguage.googleapis.com/v1beta").rstrip("/")

    def _is_mock(self, request: InferenceRequest | None = None) -> bool:
        if not self.api_key or "mock" in self.api_key.lower() or self.api_key in ("test-key", "test"):
            return True
        if request and request.metadata and request.metadata.get("mock") is True:
            return True
        return False

    async def generate(
        self,
        *,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> InferenceResponse:
        request_obj = request or InferenceRequest(model=model or "gemini-1.5-flash", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or "gemini-1.5-flash"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            created_at = datetime.now(timezone.utc)
            return InferenceResponse(
                id=f"gemini_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text=f"[gemini:{model_name}] {prompt_text}",
                usage=Usage(
                    prompt_tokens=max(1, len(prompt_text.split())),
                    completion_tokens=max(1, len(prompt_text.split())),
                    total_tokens=max(1, len(prompt_text.split())) * 2,
                ),
                finish_reason="STOP",
                latency_ms=0.0,
                created=created_at,
                metadata={"base_url": self.base_url, "provider_version": "v1beta", "cached": False, **kwargs},
                request_id=kwargs.get("request_id"),
            )

        start_time = time.perf_counter()
        endpoint = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"

        contents = []
        system_instruction = None
        for msg in request_obj.messages:
            role = "user" if msg.role in ("user", "human") else ("model" if msg.role in ("assistant", "ai") else "user")
            if msg.role == "system":
                system_instruction = {"parts": [{"text": msg.content}]}
            else:
                contents.append({"role": role, "parts": [{"text": msg.content}]})

        if not contents and prompt_text:
            contents.append({"role": "user", "parts": [{"text": prompt_text}]})

        payload: dict[str, Any] = {"contents": contents}
        if system_instruction:
            payload["system_instruction"] = system_instruction

        generation_config: dict[str, Any] = {}
        if request_obj.temperature is not None:
            generation_config["temperature"] = request_obj.temperature
        if request_obj.top_p is not None:
            generation_config["topP"] = request_obj.top_p
        if request_obj.max_tokens is not None:
            generation_config["maxOutputTokens"] = request_obj.max_tokens
        if request_obj.stop:
            generation_config["stopSequences"] = request_obj.stop if isinstance(request_obj.stop, list) else [request_obj.stop]
        if generation_config:
            payload["generationConfig"] = generation_config

        async with httpx.AsyncClient(timeout=30.0) as client:
            max_attempts = 3
            backoff_delays = [0.5, 1.0, 2.0]
            for attempt in range(max_attempts):
                try:
                    response = await client.post(endpoint, json=payload)
                    if response.status_code in (429, 503) and attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue

                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    if response.status_code != 200:
                        raise ProviderUnavailableException(f"Gemini error status {response.status_code}: {response.text}")

                    resp_json = response.json()
                    candidates = resp_json.get("candidates", [])
                    if not candidates:
                        raise ProviderUnavailableException("Gemini returned response with no candidates")

                    candidate = candidates[0]
                    content_parts = candidate.get("content", {}).get("parts", [])
                    text_content = "".join(part.get("text", "") for part in content_parts)
                    finish_reason = candidate.get("finishReason", "STOP")

                    usage_meta = resp_json.get("usageMetadata", {})
                    usage = Usage(
                        prompt_tokens=usage_meta.get("promptTokenCount", 0),
                        completion_tokens=usage_meta.get("candidatesTokenCount", 0),
                        total_tokens=usage_meta.get("totalTokenCount", 0),
                    )

                    return InferenceResponse(
                        id=f"gemini_{uuid.uuid4().hex[:12]}",
                        provider=self.name,
                        model=model_name,
                        text=text_content,
                        usage=usage,
                        finish_reason=finish_reason,
                        latency_ms=latency_ms,
                        created=datetime.now(timezone.utc),
                        raw_response=resp_json,
                    )
                except httpx.RequestError as exc:
                    if attempt == max_attempts - 1:
                        raise ProviderUnavailableException(f"Gemini connection failed: {exc}") from exc
                    await asyncio.sleep(backoff_delays[attempt])

            raise ProviderUnavailableException("Gemini API request failed after retries")

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        request_obj = request or InferenceRequest(model=model or "gemini-1.5-flash", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or "gemini-1.5-flash"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            words = f"[gemini:{model_name}] {prompt_text}".split()
            for word in words:
                yield InferenceResponse(
                    id=f"gemini_{uuid.uuid4().hex[:12]}",
                    provider=self.name,
                    model=model_name,
                    text=f"{word} ",
                    finish_reason=None,
                    usage=Usage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
                )
            yield InferenceResponse(
                id=f"gemini_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text="",
                finish_reason="STOP",
                usage=Usage(prompt_tokens=len(words), completion_tokens=len(words), total_tokens=len(words) * 2),
            )
            return

        endpoint = f"{self.base_url}/models/{model_name}:streamGenerateContent?key={self.api_key}&alt=sse"
        contents = [{"role": "user", "parts": [{"text": msg.content}]} for msg in request_obj.messages]
        payload = {"contents": contents}

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", endpoint, json=payload) as response:
                if response.status_code != 200:
                    raise ProviderUnavailableException(f"Gemini stream status {response.status_code}")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            evt = json.loads(data_str)
                            candidates = evt.get("candidates", [])
                            if candidates:
                                text_chunk = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                                yield InferenceResponse(
                                    id=f"gemini_{uuid.uuid4().hex[:12]}",
                                    provider=self.name,
                                    model=model_name,
                                    text=text_chunk,
                                    finish_reason=candidates[0].get("finishReason"),
                                    usage=Usage(prompt_tokens=0, completion_tokens=1, total_tokens=1),
                                )
                        except json.JSONDecodeError:
                            continue

    async def health_check(self) -> bool:
        if self._is_mock():
            return True
        try:
            endpoint = f"{self.base_url}/models?key={self.api_key}"
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(endpoint)
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(id="gemini-1.5-pro", provider="gemini", description="Google Gemini 1.5 Pro", context_window=1000000),
            ProviderModel(id="gemini-1.5-flash", provider="gemini", description="Google Gemini 1.5 Flash", context_window=1000000),
            ProviderModel(id="gemini-2.0-flash", provider="gemini", description="Google Gemini 2.0 Flash", context_window=1000000),
        ]
