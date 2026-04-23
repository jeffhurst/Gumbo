from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from gumbo.agent.runtime import GumboRuntime
from gumbo.config import Settings


async def _start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text("Gumbo is online. Send a request.")


async def _handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, runtime: GumboRuntime) -> None:
    if not update.message or not update.effective_chat:
        return
    chat_id = str(update.effective_chat.id)
    text = update.message.text or ""
    await update.message.reply_text("Processing your request…")
    state = await runtime.handle(user_id=chat_id, text=text, session_id=chat_id)

    if state.recent_tool_calls:
        tool_summary = "\n".join(f"- {rec.tool_name}: {'ok' if rec.success else 'failed'}" for rec in state.recent_tool_calls[-3:])
        await update.message.reply_text(f"Tool activity:\n{tool_summary}")

    await update.message.reply_text(state.final_response)


async def run_telegram_bot(settings: Settings) -> None:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    runtime = GumboRuntime(settings)
    app = Application.builder().token(settings.telegram_bot_token).build()

    app.add_handler(CommandHandler("start", _start))

    async def wrapped(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        await _handle_message(update, context, runtime)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, wrapped))
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    try:
        await app.updater.idle()
    finally:
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
