from __future__ import annotations

import asyncio
import logging

from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.constants import ChatAction

from gumbo.bot.handlers import BotHandlers
from gumbo.config.settings import load_settings
from gumbo.llm.client import LLMClient
from gumbo.state.history import ChatHistoryStore
from gumbo.utils.logging import configure_logging

logger = logging.getLogger(__name__)


def run() -> None:
    settings = load_settings()
    configure_logging(settings.log_level)

    llm_client = LLMClient(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
        temperature=settings.temperature,
    )
    history_store = ChatHistoryStore(max_messages=settings.max_history_messages)
    handlers = BotHandlers(llm_client, history_store)

    async def on_startup(application: Application) -> None:
        if settings.telegram_boot_chat_id is None:
            logger.info(
                "Skipping automatic boot greeting because TELEGRAM_BOOT_CHAT_ID is not set."
            )
            return

        await application.bot.send_chat_action(
            chat_id=settings.telegram_boot_chat_id,
            action=ChatAction.TYPING,
        )
        await handlers.send_boot_greeting_to_chat(
            chat_id=settings.telegram_boot_chat_id,
            send_text=lambda text: application.bot.send_message(
                chat_id=settings.telegram_boot_chat_id,
                text=text,
            ),
        )

    application = (
        Application.builder().token(settings.telegram_bot_token).post_init(on_startup).build()
    )
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help))
    application.add_handler(CommandHandler("reset", handlers.reset))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.handle_text)
    )

    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())

    application.run_polling(close_loop=False)
