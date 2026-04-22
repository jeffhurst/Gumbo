from __future__ import annotations


def chunk_text(value: str, chunk_size: int = 4000) -> list[str]:
    if not value:
        return [""]

    chunks: list[str] = []
    for start in range(0, len(value), chunk_size):
        chunks.append(value[start : start + chunk_size])
    return chunks
