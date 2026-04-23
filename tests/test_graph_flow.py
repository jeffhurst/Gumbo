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


@pytest.mark.asyncio
async def test_graph_uses_file_write_for_file_save_task(tmp_path):
    settings = Settings(
        GUMBO_DB_PATH=str(tmp_path / "gumbo.db"),
        GUMBO_TRACES_PATH=str(tmp_path / "traces.jsonl"),
        GUMBO_WORKSPACE_ROOT=str(tmp_path),
    )
    runtime = GumboRuntime(settings)
    state = await runtime.handle(user_id="u1", text='use file_write to save "hello world" to test.txt')

    assert state.status.value == "completed"
    assert any(call.tool_name == "file_write" and call.success for call in state.recent_tool_calls)
    assert (tmp_path / "test.txt").read_text(encoding="utf-8") == "hello world"
