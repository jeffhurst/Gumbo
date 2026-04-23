from __future__ import annotations

import uuid

from gumbo.agent.services import IntentClassifier, Planner, Reflector
from gumbo.config import Settings
from gumbo.graph.workflow import GumboGraph
from gumbo.llm.ollama import OllamaAdapter
from gumbo.logging.traces import TraceLogger
from gumbo.memory.manager import LongTermMemory, ShortTermMemory
from gumbo.models.state import AgentState
from gumbo.storage.sqlite_store import SQLiteStore
from gumbo.tools.registry import ToolRegistry


class GumboRuntime:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.store = SQLiteStore(settings.gumbo_db_path)
        self.llm = OllamaAdapter(settings.ollama_base_url, settings.ollama_model, settings.ollama_timeout_seconds)
        self.tracer = TraceLogger(settings.gumbo_traces_path)
        self.short_memory = ShortTermMemory()
        self.long_memory = LongTermMemory(self.store)
        self.tools = ToolRegistry(settings)
        self.graph = GumboGraph(
            classifier=IntentClassifier(self.llm),
            planner=Planner(self.llm),
            reflector=Reflector(self.llm),
            tools=self.tools,
            short_memory=self.short_memory,
            long_memory=self.long_memory,
            tracer=self.tracer,
        )

    async def handle(self, user_id: str, text: str, session_id: str | None = None) -> AgentState:
        sid = session_id or str(uuid.uuid4())
        state = AgentState(session_id=sid, user_id=user_id, raw_input=text)
        result = await self.graph.run(state)
        self.store.execute(
            """
            INSERT OR REPLACE INTO sessions (id, user_id, latest_input, latest_output, status)
            VALUES (?, ?, ?, ?, ?)
            """,
            (result.session_id, user_id, text, result.final_response, result.status.value),
        )
        return result
