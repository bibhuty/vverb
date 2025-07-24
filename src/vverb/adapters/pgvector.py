import os, asyncpg
from typing import Any
from .base import BaseAdapter          # ← relative import (dot = same package)

# … keep DEFAULT_PORT etc …

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
        host: str | None = None,
        port: int | None = None,
        database: str | None = None,
        user: str | None = None,
        password: str | None = None,
        min_size: int = 1,
        max_size: int = 10,
        **kw: Any,
    ) -> "PgVectorAdapter":

        host = host or os.getenv("PGV_HOST", "localhost")
        port = port or int(os.getenv("PGV_PORT", 5432))
        database = database or os.getenv("PGV_DB", "postgres")
        user = user or os.getenv("PGV_USER")
        password = password or os.getenv("PGV_PASS")


        # asyncpg accepts either DSN or individual params
        pool = await asyncpg.create_pool(
            host= host,
            port= port,
            database= database,
            user= user,
            password= password,
            min_size=min_size,
            max_size=max_size,
        )
        return cls(pool, dsn=dsn, host=host, port=port, database=database, user=user)

    # ---------------------- async context manager --------------------- #
    async def __aenter__(self):  # so you can:  async with await connect() as db:
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()

    async def close(self):
        """Close the underlying asyncpg pool."""
        await self.pool.close()

    # ---------------- verbs (stubs) --------------
    async def create_collection(self, *a, **k): ...

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