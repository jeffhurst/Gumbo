from __future__ import annotations

from typing import Any

from gumbo.config import Settings
from gumbo.tools.base import Tool
from gumbo.tools.file_ops import FileReadTool, FileWriteTool
from gumbo.tools.shell import ShellTool
from gumbo.tools.web_search import WebSearchTool


class ToolRegistry:
    def __init__(self, settings: Settings):
        self.tools: dict[str, Tool] = {
            "shell": ShellTool(settings.gumbo_workspace_root, settings.shell_timeout_seconds, settings.shell_confirm_dangerous),
            "file_read": FileReadTool(settings.gumbo_workspace_root),
            "file_write": FileWriteTool(settings.gumbo_workspace_root),
            "web_search": WebSearchTool(settings.web_search_provider, settings.web_search_base_url),
        }

    async def run(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        tool = self.tools.get(name)
        if not tool:
            return {"ok": False, "error": f"Unknown tool: {name}"}
        return await tool.run(**args)

    def describe(self) -> list[dict[str, str]]:
        return [{"name": tool.name, "description": tool.description} for tool in self.tools.values()]
