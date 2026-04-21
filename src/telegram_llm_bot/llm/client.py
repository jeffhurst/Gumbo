from __future__ import annotations

from collections.abc import Sequence

from openai import AsyncOpenAI


class LLMClient:
    def __init__(
        self, base_url: str, api_key: str, model: str, system_prompt: str, temperature: float
    ) -> None:
        normalized_base_url = base_url.rstrip("/")
        self._client = AsyncOpenAI(api_key=api_key, base_url=f"{normalized_base_url}/v1")
        self._model = model
        self._system_prompt = system_prompt
        self._temperature = temperature

    async def generate_reply(self, user_message: str, chat_history: Sequence[dict[str, str]]) -> str:
        messages = [{"role": "system", "content": self._system_prompt}, *chat_history]
        messages.append({"role": "user", "content": user_message})

        response = await self._client.chat.completions.create(
            model=self._model,
            temperature=self._temperature,
            messages=messages,
        )
        content = response.choices[0].message.content
        if isinstance(content, list):
            content = "".join(part.text for part in content if getattr(part, "type", None) == "text")
        return (content or "").strip() or "I could not generate a response."
