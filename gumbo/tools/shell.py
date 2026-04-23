from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from gumbo.tools.base import Tool


DANGEROUS_TOKENS = {"rm -rf /", "shutdown", "reboot", ":(){:|:&};:"}


class ShellTool(Tool):
    name = "shell"
    description = "Execute shell command with timeout and safety checks"

    def __init__(self, workspace_root: Path, timeout_seconds: int = 45, confirm_dangerous: bool = False):
        self.workspace_root = workspace_root.resolve()
        self.timeout_seconds = timeout_seconds
        self.confirm_dangerous = confirm_dangerous

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        command = str(kwargs.get("command", "")).strip()
        if not command:
            return {"ok": False, "error": "Empty command"}
        if any(token in command for token in DANGEROUS_TOKENS):
            if self.confirm_dangerous:
                return {"ok": False, "error": "Dangerous command requires confirmation"}
            return {"ok": False, "error": "Dangerous command blocked by policy"}

        proc = await asyncio.create_subprocess_shell(
            command,
            cwd=str(self.workspace_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=self.timeout_seconds)
        except TimeoutError:
            proc.kill()
            return {"ok": False, "error": f"Command timed out after {self.timeout_seconds}s"}

        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": stdout.decode("utf-8", errors="replace"),
            "stderr": stderr.decode("utf-8", errors="replace"),
        }
