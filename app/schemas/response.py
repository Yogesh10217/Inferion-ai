from pydantic import BaseModel, Field


class ChatCompletionChoiceMessage(BaseModel):
    """Message payload contained in a chat completion choice."""

    role: str = Field(default="assistant", description="The role of the generated message.")
    content: str = Field(..., description="The content of the generated message.")


class Choice(BaseModel):
    """A single completion choice in an OpenAI-compatible response."""

    index: int = Field(..., ge=0, description="The index of the choice.")
    message: ChatCompletionChoiceMessage = Field(..., description="The generated message.")
    finish_reason: str | None = Field(default=None, description="The reason the generation stopped.")


class Usage(BaseModel):
    """Token usage statistics for a completion response."""

    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)


class ChatCompletionResponse(BaseModel):
    """OpenAI-compatible chat completion response model."""

    id: str = Field(..., description="Unique identifier for the completion.")
    object: str = Field(default="chat.completion", description="The object type.")
    created: int = Field(..., description="Unix timestamp of the completion creation time.")
    model: str = Field(..., description="The model used to generate the completion.")
    choices: list[Choice] = Field(..., description="The list of completion choices.")
    usage: Usage | None = Field(default=None, description="Token usage statistics for the request.")


class ModelInfo(BaseModel):
    """A single entry in the OpenAI-compatible models list response."""

    id: str = Field(..., description="The model identifier.")
    object: str = Field(default="model", description="The object type.")
    created: int | None = Field(default=None, description="Unix timestamp of model creation.")
    owned_by: str = Field(default="system", description="The owner of the model.")


class ModelListResponse(BaseModel):
    """OpenAI-compatible models list response."""

    object: str = Field(default="list", description="The object type.")
    data: list[ModelInfo] = Field(..., description="A list of model objects.")
