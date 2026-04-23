from __future__ import annotations

from typing import Any

import httpx

from gumbo.tools.base import Tool


class WebSearchTool(Tool):
    name = "web_search"
    description = "Search the web and return normalized search results"

    def __init__(self, provider: str = "duckduckgo", base_url: str = "https://duckduckgo.com/html/"):
        self.provider = provider
        self.base_url = base_url

    async def run(self, **kwargs: Any) -> dict[str, Any]:
        query = str(kwargs.get("query", "")).strip()
        if not query:
            return {"ok": False, "error": "query is required"}

        if self.provider.lower() == "searxng":
            url = self.base_url.rstrip("/") + "/search"
            params = {"q": query, "format": "json"}
            async with httpx.AsyncClient(timeout=20) as client:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
            results = [
                {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
                for r in data.get("results", [])[:5]
            ]
            return {"ok": True, "provider": "searxng", "results": results}

        # DuckDuckGo-lite provider via instant answer API for reliability.
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get("https://api.duckduckgo.com/", params={"q": query, "format": "json", "no_html": 1})
            resp.raise_for_status()
            data = resp.json()
        related = data.get("RelatedTopics", [])
        results: list[dict[str, str]] = []
        for item in related:
            if "Text" in item and "FirstURL" in item:
                results.append({"title": item["Text"][:80], "url": item["FirstURL"], "snippet": item["Text"]})
            if len(results) >= 5:
                break
        if not results and data.get("AbstractURL"):
            results.append({"title": data.get("Heading", query), "url": data.get("AbstractURL", ""), "snippet": data.get("AbstractText", "")})
        return {"ok": True, "provider": "duckduckgo", "results": results}
