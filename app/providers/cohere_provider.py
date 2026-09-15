"""
Cohere Provider implementation.
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


class CohereProvider(BaseProvider):
    """Provider for Cohere API (command-r-plus, command-r, command-r-08-2024)."""

    name = "cohere"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.cohere_api_key
        self.base_url = (base_url or "https://api.cohere.com/v2").rstrip("/")

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
        request_obj = request or InferenceRequest(model=model or "command-r-plus", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or "command-r-plus"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            created_at = datetime.now(timezone.utc)
            return InferenceResponse(
                id=f"cohere_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text=f"[cohere:{model_name}] {prompt_text}",
                usage=Usage(
                    prompt_tokens=max(1, len(prompt_text.split())),
                    completion_tokens=max(1, len(prompt_text.split())),
                    total_tokens=max(1, len(prompt_text.split())) * 2,
                ),
                finish_reason="COMPLETE",
                latency_ms=0.0,
                created=created_at,
                metadata={"base_url": self.base_url, "provider_version": "v2", "cached": False, **kwargs},
                request_id=kwargs.get("request_id"),
            )

        start_time = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        messages_payload = [{"role": msg.role, "content": msg.content} for msg in request_obj.messages]
        if not messages_payload and prompt_text:
            messages_payload.append({"role": "user", "content": prompt_text})

        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages_payload,
        }
        if request_obj.temperature is not None:
            payload["temperature"] = request_obj.temperature
        if request_obj.max_tokens is not None:
            payload["max_tokens"] = request_obj.max_tokens

        async with httpx.AsyncClient(timeout=30.0) as client:
            max_attempts = 3
            backoff_delays = [0.5, 1.0, 2.0]
            for attempt in range(max_attempts):
                try:
                    response = await client.post(f"{self.base_url}/chat", json=payload, headers=headers)
                    if response.status_code in (429, 503) and attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue

                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    if response.status_code != 200:
                        raise ProviderUnavailableException(f"Cohere error status {response.status_code}: {response.text}")

                    resp_json = response.json()
                    msg_content = resp_json.get("message", {}).get("content", [])
                    text_content = "".join(item.get("text", "") for item in msg_content if item.get("type") == "text")
                    if not text_content and "text" in resp_json:
                        text_content = resp_json.get("text", "")

                    usage_tokens = resp_json.get("usage", {}).get("tokens", {})
                    input_tokens = usage_tokens.get("input_tokens", 0)
                    output_tokens = usage_tokens.get("output_tokens", 0)

                    return InferenceResponse(
                        id=resp_json.get("id", f"cohere_{uuid.uuid4().hex[:12]}"),
                        provider=self.name,
                        model=model_name,
                        text=text_content,
                        usage=Usage(
                            prompt_tokens=input_tokens,
                            completion_tokens=output_tokens,
                            total_tokens=input_tokens + output_tokens,
                        ),
                        finish_reason=resp_json.get("finish_reason", "COMPLETE"),
                        latency_ms=latency_ms,
                        created=datetime.now(timezone.utc),
                        raw_response=resp_json,
                    )
                except httpx.RequestError as exc:
                    if attempt == max_attempts - 1:
                        raise ProviderUnavailableException(f"Cohere connection failed: {exc}") from exc
                    await asyncio.sleep(backoff_delays[attempt])

            raise ProviderUnavailableException("Cohere API request failed after retries")

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        request_obj = request or InferenceRequest(model=model or "command-r-plus", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or "command-r-plus"
        prompt_text = prompt or self._extract_prompt(request_obj)

        if self._is_mock(request_obj):
            words = f"[cohere:{model_name}] {prompt_text}".split()
            for word in words:
                yield InferenceResponse(
                    id=f"cohere_{uuid.uuid4().hex[:12]}",
                    provider=self.name,
                    model=model_name,
                    text=f"{word} ",
                    finish_reason=None,
                    usage=Usage(prompt_tokens=1, completion_tokens=1, total_tokens=2),
                )
            yield InferenceResponse(
                id=f"cohere_{uuid.uuid4().hex[:12]}",
                provider=self.name,
                model=model_name,
                text="",
                finish_reason="COMPLETE",
                usage=Usage(prompt_tokens=len(words), completion_tokens=len(words), total_tokens=len(words) * 2),
            )
            return

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages_payload = [{"role": msg.role, "content": msg.content} for msg in request_obj.messages]
        payload = {
            "model": model_name,
            "messages": messages_payload,
            "stream": True,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.base_url}/chat", headers=headers, json=payload) as response:
                if response.status_code != 200:
                    raise ProviderUnavailableException(f"Cohere stream status {response.status_code}")
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if not data_str:
                            continue
                        try:
                            evt = json.loads(data_str)
                            evt_type = evt.get("type")
                            if evt_type == "content-delta":
                                delta_text = evt.get("delta", {}).get("message", {}).get("content", {}).get("text", "")
                                yield InferenceResponse(
                                    id=f"cohere_{uuid.uuid4().hex[:12]}",
                                    provider=self.name,
                                    model=model_name,
                                    text=delta_text,
                                    finish_reason=None,
                                    usage=Usage(prompt_tokens=0, completion_tokens=1, total_tokens=1),
                                )
                            elif evt_type == "message-end":
                                yield InferenceResponse(
                                    id=f"cohere_{uuid.uuid4().hex[:12]}",
                                    provider=self.name,
                                    model=model_name,
                                    text="",
                                    finish_reason="COMPLETE",
                                    usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
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
            ProviderModel(id="command-r-plus", provider="cohere", description="Cohere Command R+", context_window=128000),
            ProviderModel(id="command-r", provider="cohere", description="Cohere Command R", context_window=128000),
        ]
