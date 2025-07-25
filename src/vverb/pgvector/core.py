"""
PGVector adapter implementation for vverb.

Implements the five core verbs:
    • connect  • create_collection  • upsert  • query  • delete
plus capability negotiation.
"""

from __future__ import annotations

import asyncpg
from asyncpg import Connection
from contextlib import asynccontextmanager
from typing import Any

from .mapping import TYPE_MAP, METRIC_OPCLASS
from ..base import BaseAdapter          # vverb.adapters.base
from vverb._log import logger as _root_logger
from ..util.schema import TableSchema

log = _root_logger.getChild("pgvector")

__all__ = ["PgVectorAdapter"]


class PgVectorAdapter(BaseAdapter):
    """
    Concrete adapter for pgvector.

    Parameters accepted by `connect`
    --------------------------------
    host : str                 Postgres host, default "localhost"
    port : int                 Port, default 5432
    database : str | None      DB name; default "postgres"
    user : str | None          User; default same as OS user
    password : str | None      Password
    min_pool_size : int        Pool min connections (default 1)
    max_pool_size : int        Pool max connections (default 5)
    """

    # ------------------------------------------------------------------ #
    # construction helpers                                               #
    # ------------------------------------------------------------------ #
    def __init__(self, pool: asyncpg.Pool, **cfg: Any):
        self.pool = pool
        self.cfg = cfg  # keep original config for debugging

    # ---------- factory (class method) -------------------------------- #
    @classmethod
    async def connect(
        cls,
        *,
        dsn: str | None = None,
        min_pool_size: int = 1,
        max_pool_size: int = 1,
        **kw: Any,
    ) -> "PgVectorAdapter":
        """Create (or fetch) an asyncpg pool and return an adapter instance."""
        log.info("Connecting to pgvector database…")

        # asyncpg accepts either a DSN or individual params
        pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=int(min_pool_size),
            max_size=int(max_pool_size),
        )

        adapter = cls(pool, dsn=dsn)
        await adapter._ensure_vector_extension()
        return adapter

    # ---------------------- async context manager --------------------- #
    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        """Close the underlying asyncpg pool."""
        await self.pool.close()

    # ------------------------------------------------------------------
    # create_collection
    # ------------------------------------------------------------------
    async def create_collection(
        self,
        schema: TableSchema,
        *,
        skip_if_exists: bool = True,
        **kwargs: Any,
    ) -> None:
        """
        Create a Postgres table with a vector column and an HNSW index.
        """
        opclass = METRIC_OPCLASS.get(schema.vector.metric)
        if opclass is None:
            raise ValueError(
                f"Metric '{schema.vector.metric}' not supported by pgvector"
            )

        # ---- build column list ----
        col_defs: list[str] = [
            f"{schema.id_field} TEXT PRIMARY KEY",
            f"{schema.vector.name} VECTOR({schema.vector.dim})",
        ]

        for fld in schema.fields:
            sql_type = TYPE_MAP[fld.ftype]
            extras = ""
            if fld.not_null:
                extras += " NOT NULL"
            if fld.default is not None:
                extras += f" DEFAULT {fld.default}"
            col_defs.append(f"{fld.name} {sql_type}{extras}")

        ddl = (
            f"CREATE TABLE {'IF NOT EXISTS' if skip_if_exists else ''} "
            f"{schema.table} ({', '.join(col_defs)});"
        )

        index = (
            f"CREATE INDEX IF NOT EXISTS {schema.table}_{schema.vector.name}_idx "
            f"ON {schema.table} USING hnsw "
            f"({schema.vector.name} {opclass});"
        )

        # ---- execute ----
        async with self.pool.acquire() as conn:  # type: Connection
            await conn.execute(ddl)
            await conn.execute(index)

    # ------------------------------------------------------------------
    # stub implementations for the remaining verbs
    # ------------------------------------------------------------------
    async def upsert(self, *a, **k):  # TODO
        ...

    async def query(self, *a, **k):  # TODO
        return []

    async def delete(self, *a, **k):  # TODO
        ...

    # ------------------------------------------------------------------
    # capability probe
    # ------------------------------------------------------------------
    def capabilities(self) -> dict[str, Any]:
        return {
            "filter": False,
            "max_batch": 5000,
            "metrics": ["cosine", "l2", "ip"],
        }

    # ------------------------------------------------------------------
    # helper utilities
    # ------------------------------------------------------------------
    @asynccontextmanager
    async def raw(self):
        """Yield a borrowed asyncpg connection and release it automatically."""
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)

    async def _ensure_vector_extension(self):
        """Install pgvector extension if not already present."""
        async with self.pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    async def create_table(self, name: str, dim: int, metric: str):
        """Legacy helper kept for backward-compat tests."""
        async with self.pool.acquire() as conn:
            await conn.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {name} (
                    id TEXT PRIMARY KEY,
                    embedding VECTOR({dim}) USING {metric}
                );
                """
            )