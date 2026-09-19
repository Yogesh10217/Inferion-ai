"""
Anthropic Claude Provider implementation.
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


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic Claude API (claude-3-5-sonnet, claude-3-haiku, etc.)."""

    name = "anthropic"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.anthropic_api_key
        self.base_url = (base_url or "https://api.anthropic.com/v1").rstrip("/")

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
            model=model or "claude-3-5-sonnet-20241022", messages=[ChatMessage(role="user", content=prompt or "")]
        )
        model_name = request_obj.model or model or "claude-3-5-sonnet-20241022"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            created_at = datetime.now(timezone.utc)
            return InferenceResponse(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text=f"[anthropic:{model_name}] {prompt_text}",
                usage=Usage(
                    prompt_tokens=max(1, len(prompt_text.split())),
                    completion_tokens=max(1, len(prompt_text.split())),
                    total_tokens=max(1, len(prompt_text.split())) * 2,
                ),
                finish_reason="end_turn",
                latency_ms=0.0,
                created=created_at,
                metadata={"base_url": self.base_url, "provider_version": "v1", "cached": False, **kwargs},
                request_id=kwargs.get("request_id"),
            )

        start_time = time.perf_counter()
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }

        system_prompt = None
        messages_payload = []
        for msg in request_obj.messages:
            if msg.role == "system":
                system_prompt = msg.content
            else:
                messages_payload.append({"role": msg.role, "content": msg.content})

        if not messages_payload and prompt_text:
            messages_payload.append({"role": "user", "content": prompt_text})

        payload: dict[str, Any] = {
            "model": model_name,
            "max_tokens": request_obj.max_tokens or 1024,
            "messages": messages_payload,
        }
        if system_prompt:
            payload["system"] = system_prompt
        if request_obj.temperature is not None:
            payload["temperature"] = request_obj.temperature
        if request_obj.top_p is not None:
            payload["top_p"] = request_obj.top_p
        if request_obj.stop:
            payload["stop_sequences"] = request_obj.stop if isinstance(request_obj.stop, list) else [request_obj.stop]

        async with httpx.AsyncClient(timeout=30.0) as client:
            max_attempts = 3
            backoff_delays = [0.5, 1.0, 2.0]
            for attempt in range(max_attempts):
                try:
                    response = await client.post(
                        f"{self.base_url}/messages",
                        headers=headers,
                        json=payload,
                    )
                    if response.status_code in (429, 503) and attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue

                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    if response.status_code != 200:
                        raise ProviderUnavailableException(
                            f"Anthropic error status {response.status_code}: {response.text}"
                        )

                    resp_json = response.json()
                    content_blocks = resp_json.get("content", [])
                    text_content = "".join(b.get("text", "") for b in content_blocks if b.get("type") == "text")
                    usage_data = resp_json.get("usage", {})
                    input_tokens = usage_data.get("input_tokens", 0)
                    output_tokens = usage_data.get("output_tokens", 0)

                    return InferenceResponse(
                        id=resp_json.get("id", f"msg_{uuid.uuid4().hex[:12]}"),
                        provider=self.name,
                        model=resp_json.get("model", model_name),
                        text=text_content,
                        usage=Usage(
                            prompt_tokens=input_tokens,
                            completion_tokens=output_tokens,
                            total_tokens=input_tokens + output_tokens,
                        ),
                        finish_reason=resp_json.get("stop_reason", "end_turn"),
                        latency_ms=latency_ms,
                        created=datetime.now(timezone.utc),
                        raw_response=resp_json,
                    )
                except httpx.RequestError as exc:
                    if attempt == max_attempts - 1:
                        raise ProviderUnavailableException(f"Anthropic connection failed: {exc}") from exc
                    await asyncio.sleep(backoff_delays[attempt])

            raise ProviderUnavailableException("Anthropic API request failed after retries")

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        request_obj = request or InferenceRequest(
            model=model or "claude-3-5-sonnet-20241022", messages=[ChatMessage(role="user", content=prompt or "")]
        )
        model_name = request_obj.model or model or "claude-3-5-sonnet-20241022"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            words = f"[anthropic:{model_name}] {prompt_text}".split()
            for word in words:
                yield InferenceResponse(
                    id=f"msg_{uuid.uuid4().hex[:12]}",
                    provider=self.name,
                    model=model_name,
                    text=f"{word} ",
                    finish_reason=None,
                    usage=Usage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
                )
            yield InferenceResponse(
                id=f"msg_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text="",
                finish_reason="end_turn",
                usage=Usage(prompt_tokens=len(words), completion_tokens=len(words), total_tokens=len(words) * 2),
            )
            return

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        messages_payload = [
            {"role": msg.role, "content": msg.content} for msg in request_obj.messages if msg.role != "system"
        ]
        payload = {
            "model": model_name,
            "max_tokens": request_obj.max_tokens or 1024,
            "messages": messages_payload,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.base_url}/messages", headers=headers, json=payload) as response:
                if response.status_code != 200:
                    raise ProviderUnavailableException(f"Anthropic stream status {response.status_code}")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            evt = json.loads(data_str)
                            evt_type = evt.get("type")
                            if evt_type == "content_block_delta":
                                delta_text = evt.get("delta", {}).get("text", "")
                                yield InferenceResponse(
                                    id=f"msg_{uuid.uuid4().hex[:12]}",
                                    provider=self.name,
                                    model=model_name,
                                    text=delta_text,
                                    finish_reason=None,
                                    usage=Usage(prompt_tokens=0, completion_tokens=1, total_tokens=1),
                                )
                            elif evt_type == "message_stop":
                                yield InferenceResponse(
                                    id=f"msg_{uuid.uuid4().hex[:12]}",
                                    provider=self.name,
                                    model=model_name,
                                    text="",
                                    finish_reason="end_turn",
                                    usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
                                )
                        except json.JSONDecodeError:
                            continue

    async def health_check(self) -> bool:
        if self._is_mock():
            return True
        try:
            headers = {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/models", headers=headers)
                return res.status_code in (200, 400, 401)
        except Exception:
            return False

    async def list_models(self) -> list[ProviderModel]:
        return [
            ProviderModel(
                id="claude-3-5-sonnet-20241022",
                provider="anthropic",
                description="Anthropic Claude 3.5 Sonnet",
                context_window=200000,
            ),
            ProviderModel(
                id="claude-3-5-haiku-20241022",
                provider="anthropic",
                description="Anthropic Claude 3.5 Haiku",
                context_window=200000,
            ),
            ProviderModel(
                id="claude-3-opus-20240229",
                provider="anthropic",
                description="Anthropic Claude 3 Opus",
                context_window=200000,
            ),
        ]
