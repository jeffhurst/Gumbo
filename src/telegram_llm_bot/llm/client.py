from __future__ import annotations

from collections.abc import Sequence

from openai import AsyncOpenAI


class LLMClient:
    def __init__(self, api_key: str, model: str, system_prompt: str, temperature: float) -> None:
        self._client = AsyncOpenAI(api_key=api_key)
        self._model = model
        self._system_prompt = system_prompt
        self._temperature = temperature

    async def generate_reply(self, user_message: str, chat_history: Sequence[dict[str, str]]) -> str:
        input_messages = [{"role": "system", "content": self._system_prompt}, *chat_history]
        input_messages.append({"role": "user", "content": user_message})

        response = await self._client.responses.create(
            model=self._model,
            temperature=self._temperature,
            input=input_messages,
        )
        return response.output_text.strip() or "I could not generate a response."
