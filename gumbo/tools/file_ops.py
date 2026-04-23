from __future__ import annotations

from pathlib import Path
from typing import Any

from gumbo.tools.base import Tool


class FileReadTool(Tool):
    name = "file_read"
    description = "Read text files within workspace"

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def _resolve(self, file_path: str) -> Path:
        target = (self.workspace_root / file_path).resolve()
        if self.workspace_root not in [target, *target.parents]:
            raise ValueError("Path is outside workspace boundary")
        return target

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        try:
            path = self._resolve(str(kwargs.get("path", "")))
            max_chars = int(kwargs.get("max_chars", 10000))
            start = int(kwargs.get("start", 0))
            text = path.read_text(encoding="utf-8")
            chunk = text[start : start + max_chars]
            return {"ok": True, "path": str(path), "content": chunk, "truncated": len(text) > len(chunk)}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}


class FileWriteTool(Tool):
    name = "file_write"
    description = "Write or append text files within workspace"

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root.resolve()

    def _resolve(self, file_path: str) -> Path:
        target = (self.workspace_root / file_path).resolve()
        if self.workspace_root not in [target, *target.parents]:
            raise ValueError("Path is outside workspace boundary")
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        try:
            path = self._resolve(str(kwargs.get("path", "")))
            content = str(kwargs.get("content", ""))
            mode = str(kwargs.get("mode", "overwrite"))
            if mode == "append":
                with path.open("a", encoding="utf-8") as f:
                    f.write(content)
            else:
                path.write_text(content, encoding="utf-8")
            return {"ok": True, "path": str(path), "bytes": len(content.encode("utf-8"))}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
