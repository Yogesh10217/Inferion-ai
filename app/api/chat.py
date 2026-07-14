import json
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from app.schemas.request import ChatCompletionRequest
from app.schemas.response import ChatCompletionChoiceMessage, ChatCompletionResponse, Choice, Usage
from app.services.inference_service import InferenceService, build_inference_service
from app.adapters.openai_response_adapter import OpenAIResponseAdapter, format_sse_event

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

    response = await service.complete(model_id=payload.model, prompt=payload.messages[-1].content)
    request.state.provider = response.provider
    request.state.model = response.model

    return ChatCompletionResponse(
        id="chatcmpl-placeholder",
        object="chat.completion",
        created=0,
        model=payload.model,
        choices=[
            Choice(
                index=0,
                message=ChatCompletionChoiceMessage(role="assistant", content=response.text),
                finish_reason="stop",
            )
        ],
        usage=Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0),
    )
