from __future__ import annotations

import asyncio

import typer
from rich.console import Console

from gumbo.agent.runtime import GumboRuntime
from gumbo.cli.ui import render_state
from gumbo.config import Settings
from gumbo.telegram.bot import run_telegram_bot

app = typer.Typer(help="Gumbo autonomous/semi-autonomous agent")
config_app = typer.Typer(help="Config commands")
app.add_typer(config_app, name="config")

console = Console()


def _runtime() -> GumboRuntime:
    return GumboRuntime(Settings())


@app.command("run")
def run_once(prompt: str) -> None:
    runtime = _runtime()
    state = asyncio.run(runtime.handle(user_id="cli-user", text=prompt))
    render_state(state, mode="one-shot", model_name=runtime.settings.ollama_model)


@app.command("chat")
def chat() -> None:
    runtime = _runtime()
    session_id = None
    console.print("[bold green]Gumbo interactive chat[/bold green] (/help, /status, /plan, /memory, /tools, /quit)")
    while True:
        user_in = console.input("[cyan]You > [/cyan]").strip()
        if user_in == "/quit":
            break
        if user_in == "/help":
            console.print("Commands: /help /status /plan /memory /tools /quit")
            continue
        if user_in == "/tools":
            console.print(runtime.tools.describe())
            continue
        if user_in == "/memory":
            console.print(runtime.short_memory.get_session(session_id or ""))
            continue
        state = asyncio.run(runtime.handle(user_id="cli-user", text=user_in, session_id=session_id))
        session_id = state.session_id
        if user_in == "/status":
            console.print(f"Status: {state.status.value}, Goal: {state.goal}")
            continue
        if user_in == "/plan":
            for step in state.plan:
                console.print(f"- {step.id}: {step.description} [{step.status}]")
            continue
        render_state(state, mode="interactive", model_name=runtime.settings.ollama_model)


@app.command("telegram")
def telegram_mode() -> None:
    settings = Settings()
    asyncio.run(run_telegram_bot(settings))


@app.command("inspect-memory")
def inspect_memory(user_id: str = "cli-user", query: str = "") -> None:
    runtime = _runtime()
    rows = runtime.long_memory.retrieve(user_id=user_id, query=query or "Goal")
    for row in rows:
        console.print(f"[{row.kind}] {row.content[:180]}")


@app.command("clear-memory")
def clear_memory(user_id: str = "cli-user") -> None:
    runtime = _runtime()
    runtime.long_memory.clear_user(user_id)
    console.print(f"Cleared memory for {user_id}")


@config_app.command("show")
def show_config() -> None:
    settings = Settings()
    console.print(settings.model_dump())


if __name__ == "__main__":
    app()
