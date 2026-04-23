from __future__ import annotations

from collections import defaultdict
from typing import Any

from gumbo.models.state import AgentState, MemoryRecord
from gumbo.storage.sqlite_store import SQLiteStore


class ShortTermMemory:
    def __init__(self) -> None:
        self._sessions: dict[str, dict[str, Any]] = defaultdict(dict)

    def set(self, session_id: str, key: str, value: Any) -> None:
        self._sessions[session_id][key] = value

    def get_session(self, session_id: str) -> dict[str, Any]:
        return dict(self._sessions.get(session_id, {}))

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


class LongTermMemory:
    def __init__(self, store: SQLiteStore):
        self.store = store

    def maybe_store_from_state(self, state: AgentState) -> None:
        # Guardrail: store only stable, reusable outputs.
        if len(state.final_response) < 20 or state.status.value != "completed":
            return
        record = MemoryRecord(
            user_id=state.user_id,
            kind="task_summary",
            content=f"Goal: {state.goal}\nOutcome: {state.final_response[:800]}",
            score=0.8,
        )
        self.add(record)

    def add(self, record: MemoryRecord) -> None:
        self.store.execute(
            """
            INSERT INTO long_term_memory (user_id, kind, content, score, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                record.user_id,
                record.kind,
                record.content,
                record.score,
                record.created_at.isoformat(),
            ),
        )

    def retrieve(self, user_id: str, query: str, limit: int = 5) -> list[MemoryRecord]:
        like = f"%{query[:24]}%"
        rows = self.store.query(
            """
            SELECT user_id, kind, content, score, created_at
            FROM long_term_memory
            WHERE user_id = ? AND content LIKE ?
            ORDER BY score DESC, created_at DESC
            LIMIT ?
            """,
            (user_id, like, limit),
        )
        return [
            MemoryRecord(
                user_id=row["user_id"],
                kind=row["kind"],
                content=row["content"],
                score=row["score"],
            )
            for row in rows
        ]

    def clear_user(self, user_id: str) -> None:
        self.store.execute("DELETE FROM long_term_memory WHERE user_id = ?", (user_id,))
