from fastapi import APIRouter

from app.schemas.request import ChatCompletionRequest
from app.schemas.response import ChatCompletionResponse

router = APIRouter(tags=["chat"])


@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(payload: ChatCompletionRequest) -> ChatCompletionResponse:
    """Create a chat completion response placeholder."""
    return ChatCompletionResponse(
        id="chatcmpl-placeholder",
        object="chat.completion",
        created=0,
        model=payload.model,
        choices=[
            {
                "index": 0,
                "message": {"role": "assistant", "content": "Placeholder response"},
                "finish_reason": "stop",
            }
        ],
    )
