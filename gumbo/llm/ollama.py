from __future__ import annotations

import json
from typing import Any

import httpx


class OllamaAdapter:
    def __init__(self, base_url: str, model: str, timeout_seconds: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds

    async def generate(self, prompt: str, system: str | None = None) -> str:
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")

    async def generate_json(self, prompt: str, system: str | None = None) -> dict[str, Any]:
        raw = await self.generate(prompt=prompt, system=system)
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"Model did not return JSON: {raw[:200]}")
        return json.loads(raw[start : end + 1])
