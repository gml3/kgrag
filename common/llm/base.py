from typing import Any
from pydantic import BaseModel, Field


class LitellmModelOutput(BaseModel):
    """A model representing the output from a language model."""

    content: str = Field(description="The generated text content")
    full_response: Any | None = Field(
        default=None, description="The full response from the model, if available"
    )


class LitellmModelResponse(BaseModel):
    """A model representing the response from a language model."""

    output: LitellmModelOutput = Field(description="The output from the model")
    parsed_response: BaseModel | None = Field(
        default=None, description="Parsed response from the model"
    )
    history: list = Field(
        default_factory=list,
        description="Conversation history including the prompt and response",
    )