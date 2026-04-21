import unittest
from unittest.mock import patch

import httpx

from telegram_llm_bot.llm.client import (
    LLMClient,
    LLMClientConnectionError,
    LLMClientTimeoutError,
)


class TestLLMClient(unittest.IsolatedAsyncioTestCase):
    def _make_client(self) -> LLMClient:
        return LLMClient(
            base_url="http://localhost:11434",
            model="llama3.2",
            system_prompt="You are helpful",
            temperature=0.4,
        )

    async def test_generate_reply_maps_timeout_error(self) -> None:
        client = self._make_client()

        async def raise_timeout(*args, **kwargs):
            raise httpx.ReadTimeout("timed out")

        with patch("httpx.AsyncClient.post", side_effect=raise_timeout):
            with self.assertRaises(LLMClientTimeoutError):
                await client.generate_reply("hello", [])

    async def test_generate_reply_maps_connection_error(self) -> None:
        client = self._make_client()

        async def raise_connection(*args, **kwargs):
            raise httpx.ConnectError("failed")

        with patch("httpx.AsyncClient.post", side_effect=raise_connection):
            with self.assertRaises(LLMClientConnectionError):
                await client.generate_reply("hello", [])


if __name__ == "__main__":
    unittest.main()
