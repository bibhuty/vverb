from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any
from vverb._log import logger as _root_logger

log = _root_logger.getChild("adapters.base")
class BaseAdapter(ABC):
    """All concrete adapters subclass this. Five verbs only."""

    # ───────── connection ─────────
    @classmethod
    @abstractmethod
    async def connect(cls, **cfg: Any) -> "BaseAdapter":
        ...

    async def __aenter__(self): return self
    async def __aexit__(self, exc_type, exc, tb): await self.close()

    @abstractmethod
    async def close(self): ...

    # ───────── schema ─────────
    @abstractmethod
    async def create_collection(
        self, *, schema, skip_if_exists: bool = True
    ): ...

    # ───────── CRUD verbs ────────
    @abstractmethod
    async def upsert(
        self, name: str, ids: list[str], vectors: list[list[float]],
        metadata: list[dict[str, Any]] | None = None, *,
        if_exists: str = "update"
    ): ...

    @abstractmethod
    async def query(
        self, name: str, vector: list[float], k: int,
        filter: dict[str, Any] | None = None, *,
        search_params: dict[str, Any] | None = None,
        compat: str = "strict"
    ) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def delete(self, name: str, ids: list[str]): ...

    # ───────── capability probe ──
    @abstractmethod
    def capabilities(self) -> dict[str, Any]: ...