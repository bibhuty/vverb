from __future__ import annotations
from typing import Any

class PgVectorAdapter:
    """Temporary stub so tests import; real logic comes next."""

    def __init__(self, **cfg: Any):
        self.cfg = cfg

    # ---------- factory ----------
    @classmethod
    async def connect(cls, **cfg: Any) -> "PgVectorAdapter":
        # TODO: open asyncpg pool; for now just store cfg
        return cls(**cfg)

    # ---------- verbs (no-ops) ----------
    async def create_collection(self, *a, **k): ...
    async def upsert(self, *a, **k): ...
    async def query(self, *a, **k): return []
    async def delete(self, *a, **k): ...
    async def close(self): ...
    def capabilities(self): return {"filter": False}