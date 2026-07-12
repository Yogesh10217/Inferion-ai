from typing import Literal

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """A single chat message in the OpenAI-style request payload."""

    role: Literal["system", "user", "assistant", "tool"] = Field(
        ...,
        description="The role of the message author.",
        examples=["user"],
    )
    content: str = Field(
        ...,
        description="The content of the message.",
        examples=["Hello"],
    )


class ChatCompletionRequest(BaseModel):
    """OpenAI-compatible chat completion request model."""

    model: str = Field(
        ...,
        description="The model to use for the completion.",
        examples=["gpt-4o-mini"],
    )
    messages: list[ChatMessage] = Field(
        ...,
        min_length=1,
        description="A list of messages comprising the conversation so far.",
    )
    temperature: float | None = Field(
        default=None,
        ge=0,
        le=2,
        description="Sampling temperature between 0 and 2.",
    )
    top_p: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Nucleus sampling probability threshold between 0 and 1.",
    )
    max_tokens: int | None = Field(
        default=None,
        gt=0,
        description="Maximum number of tokens to generate.",
    )
    stream: bool = Field(
        default=False,
        description="Whether to stream the response as server-sent events.",
    )
