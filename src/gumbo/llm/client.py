from __future__ import annotations

from collections.abc import Sequence

import httpx


class LLMClientError(RuntimeError):
    """Base class for recoverable LLM client failures."""


class LLMClientTimeoutError(LLMClientError):
    """Raised when the LLM request times out."""


class LLMClientConnectionError(LLMClientError):
    """Raised when the LLM service cannot be reached."""


class LLMClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        system_prompt: str,
        temperature: float,
        timeout_seconds: float = 60.0,
    ) -> None:
        normalized_base_url = base_url.rstrip("/")
        self._chat_url = f"{normalized_base_url}/api/chat"
        self._model = model
        self._system_prompt = system_prompt
        self._temperature = temperature
        self._timeout = timeout_seconds

    async def generate_reply(self, user_message: str, chat_history: Sequence[dict[str, str]]) -> str:
        messages = [{"role": "system", "content": self._system_prompt}, *chat_history]
        messages.append({"role": "user", "content": user_message})

        payload = {
            "model": self._model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": self._temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self._chat_url, json=payload)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise LLMClientTimeoutError("Timed out waiting for the LLM service") from exc
        except httpx.ConnectError as exc:
            raise LLMClientConnectionError("Could not connect to the LLM service") from exc
        except httpx.RequestError as exc:
            raise LLMClientConnectionError("Could not connect to the LLM service") from exc

        data = response.json()
        content = data.get("message", {}).get("content", "")
        return (content or "").strip() or "I could not generate a response."
