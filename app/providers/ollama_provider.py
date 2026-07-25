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
        """Return True until a real network validation is implemented."""
        return True



    async def list_models(self) -> list[ProviderModel]:
        """Return a small set of example Ollama model metadata."""
        return [
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
