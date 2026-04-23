# Gumbo

Gumbo is a production-minded MVP agent framework for local-first execution with **Ollama + LangGraph + Telegram + dynamic CLI**.

## Features

- LangGraph iterative agent loop (ingest → intent → goal → plan → execute → reflect → memory → finalize)
- Local Ollama model adapter (HTTP API)
- Rich/Typer dynamic CLI (`chat`, `run`, `telegram`, memory/config commands)
- Telegram bot interface with per-chat session IDs and progress updates
- Tooling system with structured I/O:
  - shell execution with guardrails + timeout
  - file read/write with workspace boundary checks
  - web search (DuckDuckGo instant API or SearxNG)
- Short-term memory (in-memory session snapshots)
- Long-term memory (SQLite, timestamped, relevance/recency retrieval)
- JSONL execution traces + SQLite persistence for sessions and tool calls
- Unit and integration-style tests

## Architecture Overview

```text
gumbo/
  main.py                # Typer CLI entrypoint
  config.py              # Environment-driven settings
  agent/
    runtime.py           # Runtime wiring
    services.py          # Intent/planning/reflection services
  graph/
    workflow.py          # LangGraph state machine
  llm/
    ollama.py            # Thin Ollama HTTP adapter
  tools/
    base.py
    shell.py
    file_ops.py
    web_search.py
    registry.py
  memory/
    manager.py           # short + long-term memory policies
  storage/
    sqlite_store.py      # SQLite schema + queries
  logging/
    traces.py            # JSONL event traces
  telegram/
    bot.py               # python-telegram-bot integration
tests/
```

## Setup

1. **Prereqs**
   - Python 3.11+
   - Ollama running locally

2. **Install**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

3. **Configure**

```bash
cp .env.example .env
# edit as needed
```

4. **Run**

```bash
gumbo config show
gumbo run "inspect this repo and summarize how to run it"
gumbo chat
gumbo telegram
```

## Environment Variables

- `OLLAMA_BASE_URL` (default `http://localhost:11434`)
- `OLLAMA_MODEL` (default `llama3.1:8b`)
- `OLLAMA_TIMEOUT_SECONDS`
- `TELEGRAM_BOT_TOKEN`
- `GUMBO_DB_PATH`
- `GUMBO_WORKSPACE_ROOT`
- `GUMBO_TRACES_PATH`
- `WEB_SEARCH_PROVIDER` (`duckduckgo` or `searxng`)
- `WEB_SEARCH_BASE_URL` (used by SearxNG mode)
- `SHELL_TIMEOUT_SECONDS`
- `SHELL_CONFIRM_DANGEROUS`

## CLI Commands

- `gumbo chat` - interactive mode with slash commands:
  - `/help`, `/status`, `/plan`, `/memory`, `/tools`, `/quit`
- `gumbo run "prompt"` - one-shot task
- `gumbo telegram` - run Telegram bot mode
- `gumbo inspect-memory --user-id <id> --query <text>`
- `gumbo clear-memory --user-id <id>`
- `gumbo config show`

## Memory Policy

### Short-term memory
Per-session in-memory snapshot of:
- goal
- completed/failed steps
- recent tools

### Long-term memory
Persisted in SQLite with guardrails:
- only stores successful, substantial final responses
- stores summarized goal/outcome pairs
- retrieval by lightweight relevance (`LIKE`) + recency ordering

## Tools

All tools expose structured input/output dictionaries.

- `shell`: executes command in configured workspace root with timeout, dangerous token blocklist
- `file_read`: bounded reads with optional offset
- `file_write`: overwrite or append mode
- `web_search`: normalized result schema (`title`, `url`, `snippet`)

## Telegram Flow

1. Bot receives text.
2. Creates/uses per-chat session.
3. Sends immediate progress ack.
4. Runs runtime graph.
5. Sends tool summary and final response.

## Observability

- JSONL traces (`GUMBO_TRACES_PATH`) include graph transitions and payload snippets
- SQLite records sessions and long-term memory

## Testing

```bash
pytest -q
```

Covers:
- intent classification schema behavior
- planner structure
- tool wrappers
- memory storage/retrieval
- graph transitions (direct + iterative)

## Known Limitations

- Planner/classifier currently deterministic-first for reliability (LLM hooks available for upgrades)
- Web search quality depends on provider endpoint availability
- Telegram progress is summary-based, not token streaming
- Long-term retrieval currently keyword-biased (can be replaced by embeddings)

## Future Extensions

- strict-JSON LLM planning and tool-call selection
- embedding-backed memory retrieval
- richer terminal live dashboard with Textual
- human confirmation workflow for risky tools
- persistent task queue + resumable runs
