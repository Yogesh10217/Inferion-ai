from __future__ import annotations

import asyncio
import json
from typing import Any, AsyncIterator
import httpx

from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider, ProviderModel
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import ChatMessage, InferenceRequest
from app.core.exceptions import ProviderUnavailableException


class OllamaProvider(BaseProvider):
    """Ollama provider implementation."""

    name = "ollama"

    def __init__(self, *, base_url: str | None = None) -> None:
        self.base_url = base_url or "http://localhost:11434"

    async def generate(self, *, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> InferenceResponse:
        """Return a standardized response for the prompt."""
        request_obj = request or InferenceRequest(model=model or "", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or ""
        prompt_text = prompt or self._extract_prompt(request_obj)

        is_mock = self.base_url in ("mock", "") or (request_obj.metadata and request_obj.metadata.get("mock") is True)
        if is_mock:
            created_at = datetime.now(timezone.utc)
            return InferenceResponse(
                id=f"chatcmpl-{model_name}",
                provider=self.name,
                model=model_name,
                text=f"[ollama:{model_name}] {prompt_text}",
                usage=Usage(prompt_tokens=max(1, len(prompt_text.split())), completion_tokens=max(1, len(prompt_text.split())), total_tokens=max(1, len(prompt_text.split())) * 2),
                finish_reason="stop",
                latency_ms=0.0,
                created=created_at,
                metadata={"base_url": self.base_url, "provider_version": "v1", "cached": False, **kwargs},
                request_id=kwargs.get("request_id"),
                raw_response=None,
            )

        start_time = asyncio.get_event_loop().time()
        messages = [{"role": msg.role, "content": msg.content} for msg in request_obj.messages]
        payload: dict[str, Any] = {
            "model": model_name,
            "messages": messages,
            "stream": False,
        }
        options: dict[str, Any] = {}
        if request_obj.temperature is not None:
            options["temperature"] = request_obj.temperature
        if request_obj.top_p is not None:
            options["top_p"] = request_obj.top_p
        if request_obj.max_tokens is not None:
            options["num_predict"] = request_obj.max_tokens
        if request_obj.stop is not None:
            options["stop"] = request_obj.stop if isinstance(request_obj.stop, list) else [request_obj.stop]
        if request_obj.frequency_penalty is not None:
            options["frequency_penalty"] = request_obj.frequency_penalty
        if request_obj.presence_penalty is not None:
            options["presence_penalty"] = request_obj.presence_penalty
        if options:
            payload["options"] = options

        async with httpx.AsyncClient() as client:
            max_attempts = 3
            backoff_delays = [0.5, 1.0, 2.0]
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    response = await client.post(
                        f"{self.base_url}/api/chat",
                        json=payload,
                        timeout=30.0,
                    )
                    if response.status_code in (429, 503) and attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue

                    latency_ms = (asyncio.get_event_loop().time() - start_time) * 1000.0
                    if response.status_code != 200:
                        raise ProviderUnavailableException(f"Ollama error status {response.status_code}: {response.text}")

                    resp_json = response.json()
                    message = resp_json.get("message", {})
                    content = message.get("content", "")
                    done_reason = resp_json.get("done_reason", "stop")

                    prompt_tokens = resp_json.get("prompt_eval_count", 0)
                    completion_tokens = resp_json.get("eval_count", 0)
                    usage = Usage(
                        prompt_tokens=prompt_tokens,
                        completion_tokens=completion_tokens,
                        total_tokens=prompt_tokens + completion_tokens,
                    )

                    return InferenceResponse(
                        id=f"chatcmpl-{model_name}",
                        provider=self.name,
                        model=model_name,
                        text=content,
                        usage=usage,
                        finish_reason=done_reason or "stop",
                        latency_ms=latency_ms,
                        created=datetime.now(timezone.utc),
                        metadata={"base_url": self.base_url, "provider_version": "v1", "cached": False, **kwargs},
                        request_id=request_obj.metadata.get("request_id") if request_obj.metadata else kwargs.get("request_id"),
                        raw_response=resp_json,
                    )
                except (httpx.ConnectError, httpx.TimeoutException) as exc:
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(backoff_delays[attempt])
                        continue
                    raise ProviderUnavailableException(f"Ollama connection error: {exc}") from exc
                except httpx.RequestError as exc:
                    raise ProviderUnavailableException(f"Ollama connection error: {exc}") from exc
            if last_exc:
                raise ProviderUnavailableException(f"Ollama retries exhausted: {last_exc}") from last_exc

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
        is_mock = self.base_url == "mock" or (request.metadata and request.metadata.get("mock") is True)
        
        if is_mock:
            prompt_text = self._extract_prompt(request)
            text = f"[ollama:{model_name}] {prompt_text}"
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

        # Real HTTP streaming request to Ollama
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        payload = {
            "model": request.model,
            "messages": messages,
            "stream": True,
        }
        
        options = {}
        if request.temperature is not None:
            options["temperature"] = request.temperature
        if request.top_p is not None:
            options["top_p"] = request.top_p
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        if request.stop is not None:
            options["stop"] = request.stop if isinstance(request.stop, list) else [request.stop]
        if request.frequency_penalty is not None:
            options["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            options["presence_penalty"] = request.presence_penalty
            
        if options:
            payload["options"] = options

        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=30.0,
                ) as r:
                    if r.status_code != 200:
                        error_text = await r.aread()
                        raise ProviderUnavailableException(f"Ollama error status {r.status_code}: {error_text.decode('utf-8')}")

                    async for line in r.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk_data = json.loads(line)
                            message = chunk_data.get("message", {})
                            text = message.get("content", "")
                            done = chunk_data.get("done", False)
                            done_reason = chunk_data.get("done_reason")
                            
                            usage = Usage()
                            if done:
                                prompt_tokens = chunk_data.get("prompt_eval_count", 0)
                                completion_tokens = chunk_data.get("eval_count", 0)
                                usage = Usage(
                                    prompt_tokens=prompt_tokens,
                                    completion_tokens=completion_tokens,
                                    total_tokens=prompt_tokens + completion_tokens,
                                )

                            yield InferenceResponse(
                                id=f"chatcmpl-{model_name}",
                                provider=self.name,
                                model=model_name,
                                text=text,
                                usage=usage,
                                finish_reason=done_reason or ("stop" if done else ""),
                                latency_ms=0.0,
                                created=datetime.now(timezone.utc),
                                metadata={},
                                request_id=request.metadata.get("request_id") if request.metadata else None,
                                raw_response=chunk_data,
                            )
                        except json.JSONDecodeError:
                            continue
            except httpx.RequestError as exc:
                raise ProviderUnavailableException(f"Ollama connection error: {exc}") from exc

    async def health_check(self) -> bool:
        """Return True if Ollama service is reachable or base_url is 'mock'."""
        if self.base_url in ("mock", ""):
            return True
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.base_url}/api/tags", timeout=3.0)
                return res.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[ProviderModel]:
        """Fetch model tags from Ollama API or return defaults."""
        defaults = [
            ProviderModel(
                id="llama3.1",
                provider=self.name,
                description="Ollama local Llama 3.1",
                context_window=8192,
                status="available",
            ),
            ProviderModel(
                id="mistral",
                provider=self.name,
                description="Ollama local Mistral",
                context_window=4096,
                status="available",
            ),
        ]
        if self.base_url in ("mock", ""):
            return defaults
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{self.base_url}/api/tags", timeout=3.0)
                if res.status_code == 200:
                    models_data = res.json().get("models", [])
                    models = []
                    for item in models_data:
                        m_name = item.get("name")
                        if m_name:
                            models.append(
                                ProviderModel(
                                    id=m_name,
                                    provider=self.name,
                                    description=f"Ollama Model {m_name}",
                                    context_window=8192,
                                    status="available",
                                )
                            )
                    return models if models else defaults
        except Exception:
            pass
        return defaults

