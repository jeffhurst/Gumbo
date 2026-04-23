import pytest

from gumbo.tools.file_ops import FileReadTool, FileWriteTool
from gumbo.tools.shell import ShellTool


@pytest.mark.asyncio
async def test_shell_tool_echo(tmp_path):
    tool = ShellTool(workspace_root=tmp_path)
    out = await tool.run(command="echo hello")
    assert out["ok"] is True
    assert "hello" in out["stdout"]


@pytest.mark.asyncio
async def test_file_read_write_tools(tmp_path):
    writer = FileWriteTool(workspace_root=tmp_path)
    reader = FileReadTool(workspace_root=tmp_path)

    w = await writer.run(path="notes.txt", content="abc123", mode="overwrite")
    assert w["ok"] is True

    r = await reader.run(path="notes.txt")
    assert r["ok"] is True
    assert r["content"] == "abc123"
