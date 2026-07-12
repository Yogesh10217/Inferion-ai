import pytest
from pydantic import ValidationError

from app.schemas.request import ChatCompletionRequest, ChatMessage
from app.schemas.response import Choice, ModelInfo, ModelListResponse, Usage


def test_chat_completion_request_validates_required_fields() -> None:
    payload = ChatCompletionRequest(
        model="gpt-4o-mini",
        messages=[ChatMessage(role="user", content="Hello")],
        temperature=0.7,
        top_p=0.9,
        max_tokens=256,
        stream=False,
    )

    assert payload.model == "gpt-4o-mini"
    assert len(payload.messages) == 1
    assert payload.stream is False


def test_chat_completion_request_rejects_invalid_ranges() -> None:
    with pytest.raises(ValidationError):
        ChatCompletionRequest(
            model="gpt-4o-mini",
            messages=[ChatMessage(role="user", content="Hello")],
            temperature=3.0,
            top_p=1.2,
            max_tokens=0,
        )


def test_openai_response_models_shape() -> None:
    response = Choice(index=0, message={"role": "assistant", "content": "Hi"}, finish_reason="stop")
    assert response.finish_reason == "stop"

    usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
    assert usage.total_tokens == 15

    model_info = ModelInfo(id="model-1", object="model")
    assert model_info.id == "model-1"

    model_list = ModelListResponse(object="list", data=[model_info])
    assert model_list.data[0].id == "model-1"
