import unittest
from unittest.mock import AsyncMock, Mock

from telegram_llm_bot.bot.handlers import BotHandlers


class TestBotHandlers(unittest.IsolatedAsyncioTestCase):
    async def test_start_generates_and_sends_boot_greeting(self) -> None:
        llm_client = Mock()
        llm_client.generate_reply = AsyncMock(return_value="Hello from model!")
        history_store = Mock()
        history_store.get.return_value = []

        update = Mock()
        message = Mock()
        message.chat_id = 42
        message.chat = Mock()
        message.chat.send_action = AsyncMock()
        message.reply_text = AsyncMock()
        update.message = message

        handlers = BotHandlers(llm_client, history_store)
        await handlers.start(update, context=None)

        llm_client.generate_reply.assert_awaited_once_with("Greet the User.", [])
        history_store.append_user.assert_called_once_with(42, "Greet the User.")
        history_store.append_assistant.assert_called_once_with(42, "Hello from model!")
        message.reply_text.assert_awaited_once_with("Hello from model!")

    async def test_send_boot_greeting_to_chat_uses_callback(self) -> None:
        llm_client = Mock()
        llm_client.generate_reply = AsyncMock(return_value="Welcome!")
        history_store = Mock()
        history_store.get.return_value = []
        send_text = AsyncMock()

        handlers = BotHandlers(llm_client, history_store)
        await handlers.send_boot_greeting_to_chat(chat_id=77, send_text=send_text)

        llm_client.generate_reply.assert_awaited_once_with("Greet the User.", [])
        history_store.append_user.assert_called_once_with(77, "Greet the User.")
        history_store.append_assistant.assert_called_once_with(77, "Welcome!")
        send_text.assert_awaited_once_with("Welcome!")


if __name__ == "__main__":
    unittest.main()
