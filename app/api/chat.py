import json

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.adapters.openai_response_adapter import OpenAIResponseAdapter, format_sse_event
from app.schemas.request import ChatCompletionRequest
from app.schemas.response import ChatCompletionChoiceMessage, ChatCompletionResponse, Choice, Usage
from app.services.inference_service import InferenceService, build_inference_service

router = APIRouter(tags=["chat"])


def get_inference_service(request: Request) -> InferenceService:
    """Dependency injection provider for the inference service."""
    if hasattr(request.app.state, "container"):
        return request.app.state.container.inference_service
    return build_inference_service()


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    payload: ChatCompletionRequest,
    request: Request,
    service: InferenceService = Depends(get_inference_service),
) -> ChatCompletionResponse | StreamingResponse:
    """Create a chat completion response or stream it when requested."""
    request.state.model = payload.model
    # TODO: Integrate Knowledge/Retrieval before inference here
    # Example:
    # context = retrieval_service.search(payload.messages[-1].content)
    # payload = context_builder.inject(payload, context)

    if hasattr(request.app.state, "container"):
        model_meta = request.app.state.container.registry.get_model(payload.model)
        if model_meta:
            request.state.provider = model_meta.provider

    if payload.stream:
        async def event_stream():
            try:
                async for chunk in service.stream(payload):
                    request.state.provider = chunk.provider
                    request.state.model = chunk.model
                    chunk_dict = OpenAIResponseAdapter.to_chat_completion_chunk(chunk)
                    yield format_sse_event(data=json.dumps(chunk_dict, ensure_ascii=False))
            except Exception as exc:
                raise exc

            yield format_sse_event(data="[DONE]")

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    response = await service.complete(
        model_id=payload.model,
        prompt=payload.messages[-1].content,
        metadata=payload.metadata,
    )
    request.state.provider = getattr(response, "provider", None)
    request.state.model = getattr(response, "model", payload.model)

    res_id = getattr(response, "id", None) or "chatcmpl-placeholder"
    res_usage = getattr(response, "usage", None)
    prompt_toks = getattr(res_usage, "prompt_tokens", 0) if res_usage else 0
    comp_toks = getattr(res_usage, "completion_tokens", 0) if res_usage else 0
    tot_toks = getattr(res_usage, "total_tokens", 0) if res_usage else (prompt_toks + comp_toks)

    res_created = getattr(response, "created", None)
    created_ts = (
        int(res_created.timestamp())
        if (res_created and hasattr(res_created, "timestamp"))
        else (int(res_created) if isinstance(res_created, (int, float)) else 0)
    )

    res_text = getattr(response, "text", "")
    finish_reason = getattr(response, "finish_reason", "stop") or "stop"

    return ChatCompletionResponse(
        id=res_id,
        object="chat.completion",
        created=created_ts,
        model=payload.model,
        choices=[
            Choice(
                index=0,
                message=ChatCompletionChoiceMessage(role="assistant", content=res_text),
                finish_reason=finish_reason,
            )
        ],
        usage=Usage(prompt_tokens=prompt_toks, completion_tokens=comp_toks, total_tokens=tot_toks),
    )
