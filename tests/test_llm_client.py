import unittest
from types import SimpleNamespace

import httpx
from openai import APIConnectionError, APITimeoutError

from telegram_llm_bot.llm.client import (
    LLMClient,
    LLMClientConnectionError,
    LLMClientTimeoutError,
)


class _CompletionsStub:
    def __init__(self, behavior):
        self._behavior = behavior

    async def create(self, **kwargs):
        if isinstance(self._behavior, Exception):
            raise self._behavior
        return self._behavior


class TestLLMClient(unittest.IsolatedAsyncioTestCase):
    def _make_client(self) -> LLMClient:
        return LLMClient(
            base_url="http://localhost:11434",
            api_key="ollama",
            model="llama3.2",
            system_prompt="You are helpful",
            temperature=0.4,
        )

    async def test_generate_reply_maps_timeout_error(self) -> None:
        client = self._make_client()
        request = httpx.Request("POST", "http://localhost:11434/v1/chat/completions")
        timeout_exc = APITimeoutError(request=request)
        client._client = SimpleNamespace(
            chat=SimpleNamespace(completions=_CompletionsStub(timeout_exc))
        )

        with self.assertRaises(LLMClientTimeoutError):
            await client.generate_reply("hello", [])

    async def test_generate_reply_maps_connection_error(self) -> None:
        client = self._make_client()
        request = httpx.Request("POST", "http://localhost:11434/v1/chat/completions")
        connect_exc = APIConnectionError(message="failed", request=request)
        client._client = SimpleNamespace(
            chat=SimpleNamespace(completions=_CompletionsStub(connect_exc))
        )

        with self.assertRaises(LLMClientConnectionError):
            await client.generate_reply("hello", [])


if __name__ == "__main__":
    unittest.main()
