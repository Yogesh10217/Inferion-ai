import pytest

from app.providers.openai_provider import OpenAIProvider
from app.schemas.request import ChatMessage, InferenceRequest


@pytest.mark.asyncio
async def test_openai_provider_accepts_inference_request_object() -> None:
    request = InferenceRequest(
        model="gpt-4o-mini",
        messages=[ChatMessage(role="user", content="Hello")],
        temperature=0.2,
        stream=False,
        metadata={"source": "unit-test"},
    )
    provider = OpenAIProvider()

    response = await provider.generate(request=request)

    assert response.model == "gpt-4o-mini"
    assert response.provider == "openai"
    assert "Hello" in response.text
