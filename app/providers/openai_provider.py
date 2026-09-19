from __future__ import annotations

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any, AsyncIterator

import httpx

from app.core.config import get_settings
from app.core.exceptions import ProviderUnavailableException
from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import ChatMessage, InferenceRequest


class OpenAIProvider(BaseProvider):
    """OpenAI-compatible provider implementation."""

    name = "openai"

    def __init__(self, *, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or get_settings().openai_api_key
        self.base_url = base_url or "https://api.openai.com/v1"

    async def generate(
        self,
        *,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> InferenceResponse:
        """Return a standardized response for the prompt."""
        request_obj = request or InferenceRequest(
            model=model or "", messages=[ChatMessage(role="user", content=prompt or "")]
        )
        model_name = request_obj.model or model or ""
        prompt_text = prompt or self._extract_prompt(request_obj)

        is_mock = (
            not self.api_key
            or self.api_key in ("mock", "test-key", "test")
            or (request_obj.metadata and request_obj.metadata.get("mock") is True)
        )
        if is_mock:
            created_at = datetime.now(timezone.utc)
            return InferenceResponse(
                id=f"chatcmpl-{model_name}",
                provider=self.name,
                model=model_name,
                text=f"[openai:{model_name}] {prompt_text}",
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
                raw_response=None,
            )

        start_time = time.perf_counter()
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        messages = [{"role": msg.role, "content": msg.content} for msg in request_obj.messages]
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": False,
        }
        if request_obj.temperature is not None:
            payload["temperature"] = request_obj.temperature
        if request_obj.top_p is not None:
            payload["top_p"] = request_obj.top_p
        if request_obj.max_tokens is not None:
            payload["max_tokens"] = request_obj.max_tokens
        if request_obj.stop is not None:
            payload["stop"] = request_obj.stop
        if request_obj.frequency_penalty is not None:
            payload["frequency_penalty"] = request_obj.frequency_penalty
        if request_obj.presence_penalty is not None:
            payload["presence_penalty"] = request_obj.presence_penalty

        async with httpx.AsyncClient() as client:
            max_attempts = 3
            backoff_delays = [0.5, 1.0, 2.0]
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    response = await client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload,
                        timeout=30.0,
                    )
                    if response.status_code in (429, 503) and attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue

                    latency_ms = (time.perf_counter() - start_time) * 1000.0
                    if response.status_code != 200:
                        raise ProviderUnavailableException(
                            f"OpenAI error status {response.status_code}: {response.text}"
                        )

                    resp_json = response.json()
                    choices = resp_json.get("choices", [])
                    if not choices:
                        raise ProviderUnavailableException("OpenAI returned response with no choices")

                    choice = choices[0]
                    message = choice.get("message", {})
                    content = message.get("content", "")
                    finish_reason = choice.get("finish_reason", "stop")

                    usage_data = resp_json.get("usage", {})
                    usage = Usage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                    )

                    created_timestamp = resp_json.get("created", int(time.time()))
                    created_at = datetime.fromtimestamp(created_timestamp, tz=timezone.utc)

                    return InferenceResponse(
                        id=resp_json.get("id", f"chatcmpl-{model_name}"),
                        provider=self.name,
                        model=resp_json.get("model", model_name),
                        text=content,
                        usage=usage,
                        finish_reason=finish_reason,
                        latency_ms=latency_ms,
                        created=created_at,
                        metadata={"base_url": self.base_url, "provider_version": "v1", "cached": False, **kwargs},
                        request_id=(
                            request_obj.metadata.get("request_id") if request_obj.metadata else kwargs.get("request_id")
                        ),
                        raw_response=resp_json,
                    )
                except (httpx.ConnectError, httpx.TimeoutException) as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue
                    raise ProviderUnavailableException(f"OpenAI connection error: {exc}") from exc
                except httpx.RequestError as exc:
                    raise ProviderUnavailableException(f"OpenAI connection error: {exc}") from exc
            if last_exc:
                raise ProviderUnavailableException(f"OpenAI retries exhausted: {last_exc}") from last_exc

    async def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        """Yield normalized InferenceResponse chunks for the completion."""
        if request is None:
            request = InferenceRequest(
                model=model or "", messages=[ChatMessage(role="user", content=prompt or "")], **kwargs
            )
        model_name = request.model

        # Check if we should use mock/simulation fallback or real client
        is_mock = (
            not self.api_key
            or self.api_key in ("mock", "test-key", "test")
            or (request.metadata and request.metadata.get("mock") is True)
        )

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
                        raise ProviderUnavailableException(
                            f"OpenAI error status {r.status_code}: {error_text.decode('utf-8')}"
                        )

                    async for line in r.aiter_lines():
                        if not line.strip():
                            continue
                        if line.startswith("data: "):
                            data_str = line[len("data: ") :].strip()
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
                                    created=datetime.fromtimestamp(
                                        chunk_data.get("created", int(time.time())), tz=timezone.utc
                                    ),
                                    metadata={},
                                    request_id=request.metadata.get("request_id") if request.metadata else None,
                                    raw_response=chunk_data,
                                )
                            except json.JSONDecodeError:
                                continue
            except httpx.RequestError as exc:
                raise ProviderUnavailableException(f"OpenAI connection error: {exc}") from exc

    async def health_check(self) -> bool:
        """Return True if OpenAI API endpoint responds or if running in mock mode."""
        if not self.api_key or self.api_key in ("mock", "test-key", "test"):
            return True
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.base_url}/models", headers=headers, timeout=5.0)
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[ProviderModel]:
        """Fetch models from OpenAI or return defaults."""
        defaults = [
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
        if not self.api_key or self.api_key in ("mock", "test-key", "test"):
            return defaults
        try:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.base_url}/models", headers=headers, timeout=5.0)
                if res.status_code == 200:
                    data = res.json().get("data", [])
                    models = []
                    for item in data[:20]:
                        m_id = item.get("id")
                        if m_id:
                            models.append(
                                ProviderModel(
                                    id=m_id,
                                    provider=self.name,
                                    description=f"OpenAI Model {m_id}",
                                    context_window=128000,
                                    status="available",
                                )
                            )
                    return models if models else defaults
        except Exception:
            pass
        return defaults
