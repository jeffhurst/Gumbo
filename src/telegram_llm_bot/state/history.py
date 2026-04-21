from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Sequence


class ChatHistoryStore:
    def __init__(self, max_messages: int) -> None:
        self._max_messages = max_messages
        self._store: dict[int, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=self._max_messages)
        )

    def get(self, chat_id: int) -> Sequence[dict[str, str]]:
        return list(self._store[chat_id])

    def append_user(self, chat_id: int, content: str) -> None:
        self._store[chat_id].append({"role": "user", "content": content})

    def append_assistant(self, chat_id: int, content: str) -> None:
        self._store[chat_id].append({"role": "assistant", "content": content})

    def clear(self, chat_id: int) -> None:
        self._store[chat_id].clear()
