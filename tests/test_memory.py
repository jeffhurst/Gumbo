from gumbo.memory.manager import LongTermMemory
from gumbo.models.state import MemoryRecord
from gumbo.storage.sqlite_store import SQLiteStore


def test_long_term_memory_add_retrieve(tmp_path):
    store = SQLiteStore(tmp_path / "gumbo.db")
    mem = LongTermMemory(store)
    mem.add(MemoryRecord(user_id="u1", kind="pref", content="User likes concise summaries", score=0.9))
    rows = mem.retrieve(user_id="u1", query="likes")
    assert rows
    assert rows[0].kind == "pref"
