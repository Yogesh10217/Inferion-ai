"""
Mistral Provider implementation.
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


class MistralProvider(BaseProvider):
    """Provider for Mistral API (mistral-large, mistral-small, codestral)."""

    name = "mistral"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.mistral_api_key
        self.base_url = (base_url or "https://api.mistral.ai/v1").rstrip("/")

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
        request_obj = request or InferenceRequest(
            model=model or "mistral-large-latest", messages=[ChatMessage(role="user", content=prompt or "")]
        )
        model_name = request_obj.model or model or "mistral-large-latest"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            created_at = datetime.now(timezone.utc)
            return InferenceResponse(
                id=f"mistral_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text=f"[mistral:{model_name}] {prompt_text}",
                usage=Usage(
                    prompt_tokens=max(1, len(prompt_text.split())),
                    completion_tokens=max(1, len(prompt_text.split())),
                    total_tokens=max(1, len(prompt_text.split())) * 2,
                ),
                finish_reason="stop",
                latency_ms=0.0,
                created=created_at,
                metadata={"base_url": self.base_url, "provider_version": "v1", "cached": False, **kwargs},
                request_id=kwargs.get("request_id"),
            )

        start_time = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages = [{"role": msg.role, "content": msg.content} for msg in request_obj.messages]
        if not messages and prompt_text:
            messages.append({"role": "user", "content": prompt_text})

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
        }
        if request_obj.temperature is not None:
            payload["temperature"] = request_obj.temperature
        if request_obj.top_p is not None:
            payload["top_p"] = request_obj.top_p
        if request_obj.max_tokens is not None:
            payload["max_tokens"] = request_obj.max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            max_attempts = 3
            backoff_delays = [0.5, 1.0, 2.0]
            for attempt in range(max_attempts):
                try:
                    response = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                    if response.status_code in (429, 503) and attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue

                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    if response.status_code != 200:
                        raise ProviderUnavailableException(
                            f"Mistral error status {response.status_code}: {response.text}"
                        )

                    resp_json = response.json()
                    choices = resp_json.get("choices", [])
                    if not choices:
                        raise ProviderUnavailableException("Mistral returned response with no choices")

                    choice = choices[0]
                    content = choice.get("message", {}).get("content", "")
                    finish_reason = choice.get("finish_reason", "stop")

                    usage_data = resp_json.get("usage", {})
                    usage = Usage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                    )

                    return InferenceResponse(
                        id=resp_json.get("id", f"mistral_{uuid.uuid4().hex[:12]}"),
                        provider=self.name,
                        model=resp_json.get("model", model_name),
                        text=content,
                        usage=usage,
                        finish_reason=finish_reason,
                        latency_ms=latency_ms,
                        created=datetime.now(timezone.utc),
                        raw_response=resp_json,
                    )
                except httpx.RequestError as exc:
                    if attempt == max_attempts - 1:
                        raise ProviderUnavailableException(f"Mistral connection failed: {exc}") from exc
                    await asyncio.sleep(backoff_delays[attempt])

            raise ProviderUnavailableException("Mistral API request failed after retries")

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        request_obj = request or InferenceRequest(
            model=model or "mistral-large-latest", messages=[ChatMessage(role="user", content=prompt or "")]
        )
        model_name = request_obj.model or model or "mistral-large-latest"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            words = f"[mistral:{model_name}] {prompt_text}".split()
            for word in words:
                yield InferenceResponse(
                    id=f"mistral_{uuid.uuid4().hex[:12]}",
                    provider=self.name,
                    model=model_name,
                    text=f"{word} ",
                    finish_reason=None,
                    usage=Usage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
                )
            yield InferenceResponse(
                id=f"mistral_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text="",
                finish_reason="stop",
                usage=Usage(prompt_tokens=len(words), completion_tokens=len(words), total_tokens=len(words) * 2),
            )
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = [{"role": msg.role, "content": msg.content} for msg in request_obj.messages]
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream(
                "POST", f"{self.base_url}/chat/completions", headers=headers, json=payload
            ) as response:
                if response.status_code != 200:
                    raise ProviderUnavailableException(f"Mistral stream status {response.status_code}")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        if not data_str:
                            continue
                        try:
                            evt = json.loads(data_str)
                            choices = evt.get("choices", [])
                            if choices:
                                delta_text = choices[0].get("delta", {}).get("content", "")
                                finish_reason = choices[0].get("finish_reason")
                                yield InferenceResponse(
                                    id=evt.get("id", f"mistral_{uuid.uuid4().hex[:12]}"),
                                    provider=self.name,
                                    model=model_name,
                                    text=delta_text,
                                    finish_reason=finish_reason,
                                    usage=Usage(prompt_tokens=0, completion_tokens=1, total_tokens=1),
                                )
                        except json.JSONDecodeError:
                            continue

    async def health_check(self) -> bool:
        if self._is_mock():
            return True
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/models", headers=headers)
                return res.status_code in (200, 401)
        except Exception:
            return False

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(
                id="mistral-large-latest", provider="mistral", description="Mistral Large", context_window=128000
            ),
            ProviderModel(
                id="mistral-small-latest", provider="mistral", description="Mistral Small", context_window=32000
            ),
            ProviderModel(
                id="codestral-latest", provider="mistral", description="Codestral Code Generation", context_window=32000
            ),
        ]
