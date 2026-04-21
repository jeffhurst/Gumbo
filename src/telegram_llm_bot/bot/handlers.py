from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ContextTypes

from telegram_llm_bot.llm.client import (
    LLMClient,
    LLMClientConnectionError,
    LLMClientTimeoutError,
)
from telegram_llm_bot.state.history import ChatHistoryStore
from telegram_llm_bot.utils.text import chunk_text

logger = logging.getLogger(__name__)


class BotHandlers:
    def __init__(self, llm_client: LLMClient, history_store: ChatHistoryStore) -> None:
        self._llm_client = llm_client
        self._history_store = history_store

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if update.message is None:
            return
        await update.message.reply_text(
            "Hi! Send me a message and I'll ask the LLM, then return the answer.\n"
            "Use /reset to clear the current chat memory."
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if update.message is None:
            return
        await update.message.reply_text(
            "Usage:\n"
            "- Send any text message to chat with the LLM.\n"
            "- /start for welcome message.\n"
            "- /help for this message.\n"
            "- /reset to clear chat history for this conversation."
        )

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if update.message is None:
            return

        self._history_store.clear(update.message.chat_id)
        await update.message.reply_text("Cleared chat memory for this conversation.")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        del context
        if update.message is None or not update.message.text:
            return

        user_text = update.message.text
        chat_id = update.message.chat_id
        history = self._history_store.get(chat_id)
        await update.message.chat.send_action(ChatAction.TYPING)

        try:
            model_reply = await self._llm_client.generate_reply(user_text, history)
            self._history_store.append_user(chat_id, user_text)
            self._history_store.append_assistant(chat_id, model_reply)
            for chunk in chunk_text(model_reply):
                await update.message.reply_text(chunk)
        except LLMClientTimeoutError:
            logger.warning("LLM request timed out")
            await update.message.reply_text(
                "The LLM service timed out. Please check that it is running and try again."
            )
        except LLMClientConnectionError:
            logger.warning("Could not connect to LLM service")
            await update.message.reply_text(
                "I couldn't reach the LLM service. Verify OLLAMA_BASE_URL and that the server is up."
            )
        except Exception:  # noqa: BLE001
            logger.exception("Error generating LLM response")
            await update.message.reply_text(
                "Sorry, I hit an unexpected error while processing your message."
            )
