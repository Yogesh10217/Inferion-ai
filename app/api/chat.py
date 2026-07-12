from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.schemas.request import ChatCompletionRequest
from app.schemas.response import ChatCompletionChoiceMessage, ChatCompletionResponse, Choice, Usage
from app.services.inference_service import InferenceService, build_inference_service

router = APIRouter(tags=["chat"])


def get_inference_service() -> InferenceService:
    """Dependency injection provider for the inference service."""
    return build_inference_service()


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(
    payload: ChatCompletionRequest,
    service: InferenceService = Depends(get_inference_service),
) -> ChatCompletionResponse | StreamingResponse:
    """Create a chat completion response or stream it when requested."""
    if payload.stream:
        async def event_stream():
            async for chunk in service.stream_completion(model_id=payload.model, prompt=payload.messages[-1].content):
                yield chunk.encode("utf-8")

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    response = await service.complete(model_id=payload.model, prompt=payload.messages[-1].content)
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
