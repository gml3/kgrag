"""Chat model implementation using Litellm."""

from collections.abc import Generator
from functools import partial

import litellm
from litellm import completion
from pydantic import BaseModel

from common.config.models.chat_model_config import ChatModelConfig
from common.llm.base import LitellmModelResponse, LitellmModelOutput

litellm.suppress_debug_info = True


class LitellmChatModel:

    def __init__(self, config: ChatModelConfig):
        common_kwargs = {
            "model": config.model,
            "api_key": config.api_key,
            "api_base": config.api_base,
            "max_tokens": config.max_tokens,
            "temperature": config.temperature,
            "top_p": config.top_p,
            "n": config.n,
        }
        self.completion = partial(completion, **common_kwargs)

    def chat(self, prompt: str, history: list | None = None):
        messages: list[dict[str, str]] = history or []
        messages.append({"role": "user", "content": prompt})

        response = self.completion(messages=messages, stream=False)

        messages.append({
            "role": "assistant",
            "content": response.choices[0].message.content or "",
        })

        parsed_response: BaseModel | None = None

        return LitellmModelResponse(
            output=LitellmModelOutput(content=response.choices[0].message.content or ""),
            parsed_response=parsed_response,
            history=messages,
        )

    def chat_stream(self, prompt: str, history: list | None = None) -> Generator[str, None]:
        messages: list[dict[str, str]] = history or []
        messages.append({"role": "user", "content": prompt})

        response = self.completion(messages=messages, stream=True)

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
