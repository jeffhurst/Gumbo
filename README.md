# Telegram LLM Bot (Python)

A cleanly organized Python app that wraps an LLM and exposes it through Telegram chat.

## Features
- `/start`, `/help`, and `/reset` commands
- Handles normal text messages and replies with LLM output
- Maintains bounded per-chat history for multi-turn context
- Splits long model responses into Telegram-safe chunks
- Configurable model, temperature, history size, and system prompt

## Project Structure

```text
src/telegram_llm_bot/
  main.py                 # Entry point
  app.py                  # App bootstrap and Telegram wiring
  config/settings.py      # Environment config loading + validation
  llm/client.py           # LLM provider wrapper
  bot/handlers.py         # Telegram command/message handlers
  state/history.py        # In-memory per-chat conversation store
  utils/logging.py        # Logging setup
  utils/text.py           # Message chunking utility
```

## 1) Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2) Configure

Copy `.env.example` to `.env` and fill values:

```bash
cp .env.example .env
```

Required values:
- `TELEGRAM_BOT_TOKEN`: Telegram Bot token from BotFather

Optional values:
- `OLLAMA_BASE_URL` (default: `http://localhost:11434`)
- `OLLAMA_API_KEY` (default: `ollama`; can be any non-empty value for local Ollama)
- `OLLAMA_MODEL` (default: `llama3.2`)
- `OLLAMA_TEMPERATURE` (default: `0.4`, range: `0.0` to `2.0`)
- `SYSTEM_PROMPT` (default: helpful general assistant)
- `MAX_HISTORY_MESSAGES` (default: `12`)
- `BOT_LOG_LEVEL` (default: `INFO`)

## 3) Run

```bash
telegram-llm-bot
```

or

```bash
python -m telegram_llm_bot.main
```

## Notes
- This implementation uses long polling (simple local run).
- Chat memory is in-process only and resets when the bot restarts.
- Ensure your local Ollama server is running and the configured model is pulled (example: `ollama pull llama3.2`).
- For production, consider webhook mode, durable persistence, auth controls, and rate limiting.
