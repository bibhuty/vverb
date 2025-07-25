import asyncpg
import os
from contextlib import asynccontextmanager
from typing import Any

from asyncpg import Connection

from .mapping import TYPE_MAP, METRIC_OPCLASS
from ..base import BaseAdapter  # ← relative import (dot = same package)
# ---------------- verbs (stubs) --------------
from ...util.schema import TableSchema
from vverb._log import logger as _root_logger

log = _root_logger.getChild("pgvector")
# … keep DEFAULT_PORT etc …
__all__ = ["PgVectorAdapter"]     # ←  export list lives at module level
                                  #     everything else (helper funcs,
                                  #     constants, etc.) stays “private”
class PgVectorAdapter(BaseAdapter):
    """
        Concrete adapter for pgvector.

        Parameters accepted by `connect`

        ----------
        host : str                 Postgres host, default "localhost"
        port : int                 Port, default 5432
        database : str | None      DB name; default "postgres"
        user : str | None          User; default same as OS user
        password : str | None      Password
        min_size : int             Pool min connections (default 1)
        max_size : int             Pool max connections (default 5)
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

        log.info("Connecting to pgvector database...")
        # asyncpg accepts either DSN or individual params
        pool = await asyncpg.create_pool(
            dsn=dsn,
            min_size=int(min_pool_size),
            max_size=int(max_pool_size),
        )
        adapter = cls(pool, dsn=dsn)
        await adapter._ensure_vector_extension()  # ensure pgvector extension is installed
        return adapter

    # ---------------------- async context manager --------------------- #
    async def __aenter__(self):  # so you can:  async with await connect() as db:
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        """Close the underlying asyncpg pool."""
        await self.pool.close()

    # … inside PgVectorAdapter class …

    # ------------------------------------------------------------------
    # create_collection
    # ------------------------------------------------------------------
    async def create_collection(self, schema: TableSchema, *, skip_if_exists: bool = True, **kwargs) -> None:
        """
        Create a Postgres table with a pgvector column and an HNSW index.

        Parameters
        ----------
        schema : TableSchema
            High-level description of table + vector column + scalar fields.
        skip_if_exists : bool
            If True (default) use `CREATE TABLE IF NOT EXISTS` so the call
            is idempotent.
        """
        opclass = METRIC_OPCLASS.get(schema.vector.metric)
        if opclass is None:
            raise ValueError(f"Metric '{schema.vector.metric}' not supported by pgvector")

        # ---- build column list ----
        col_defs: list[str] = [
            f"{schema.id_field} TEXT PRIMARY KEY",
            f"{schema.vector.name} VECTOR({schema.vector.dim})"
        ]

        for fld in schema.fields:
            sql_type = TYPE_MAP[fld.ftype]
            extras = ""
            if fld.not_null:
                extras += " NOT NULL"
            if fld.default is not None:
                extras += f" DEFAULT {fld.default}"
            col_defs.append(f"{fld.name} {sql_type}{extras}")

        ddl = f"""
            CREATE TABLE {"IF NOT EXISTS" if skip_if_exists else ""} {schema.table} (
                {", ".join(col_defs)}
            );
        """

        index = f"""
            CREATE INDEX IF NOT EXISTS {schema.table}_{schema.vector.name}_idx
                ON {schema.table}
             USING hnsw ({schema.vector.name} {opclass});
        """

        # ---- execute ----
        async with self.pool.acquire() as conn:  # type: Connection
            await conn.execute(ddl)
            await conn.execute(index)

    async def upsert(self, *a, **k): ...

    async def query(self, *a, **k): return []

    async def delete(self, *a, **k): ...

    # ------------- capability probe -------------
    def capabilities(self):
        return {
            "filter": False,
            "max_batch": 5000,
            "metrics": ["cosine", "l2", "ip"],
        }
    # ------------- helper methods -------------
    @asynccontextmanager
    async def raw(self):
        """Yield a borrowed asyncpg connection and release it automatically."""
        conn = await self.pool.acquire()
        try:
            yield conn
        finally:
            await self.pool.release(conn)

    async def _ensure_vector_extension(self):
        """Ensure the pgvector extension is installed."""
        async with self.pool.acquire() as conn:
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            # Note: this is a no-op if the extension already exists
            # but we need to ensure it's there before creating tables

    async def create_table(self, name: str, dim: int, metric: str):
        """
        Create a table with a vector column.
        """
        async with self.pool.acquire() as conn:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {name} (
                    id TEXT PRIMARY KEY,
                    embedding VECTOR({dim}) USING {metric}
                );
            """)
            # Note: this is a no-op if the table already exists
            # but we need to ensure the vector column is created