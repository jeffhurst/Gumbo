import pytest

from gumbo.agent.runtime import GumboRuntime
from gumbo.config import Settings


@pytest.mark.asyncio
async def test_graph_success_flow(tmp_path):
    settings = Settings(
        GUMBO_DB_PATH=str(tmp_path / "gumbo.db"),
        GUMBO_TRACES_PATH=str(tmp_path / "traces.jsonl"),
        GUMBO_WORKSPACE_ROOT=str(tmp_path),
    )
    runtime = GumboRuntime(settings)
    state = await runtime.handle(user_id="u1", text="search the web for langgraph and save results")
    assert state.status.value in {"completed", "blocked"}
    assert state.goal


@pytest.mark.asyncio
async def test_graph_direct_finalize(tmp_path):
    settings = Settings(
        GUMBO_DB_PATH=str(tmp_path / "gumbo.db"),
        GUMBO_TRACES_PATH=str(tmp_path / "traces.jsonl"),
        GUMBO_WORKSPACE_ROOT=str(tmp_path),
    )
    runtime = GumboRuntime(settings)
    async def fake_generate(prompt: str, system: str | None = None) -> str:
        return "### Favorite Foods\n- Pizza\n- Sushi"

    runtime.llm.generate = fake_generate
    state = await runtime.handle(user_id="u1", text="Hi")
    assert "Favorite Foods" in state.final_response
    assert state.final_response != state.goal
