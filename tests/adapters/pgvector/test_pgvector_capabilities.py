from __future__ import annotations

import pytest

from vverb.pgvector import connect

pytestmark = pytest.mark.asyncio


async def test_capabilities_structure(pgvector_config: tuple[str, int, int]):
    dsn, min_pool_size, max_pool_size = pgvector_config
    """
    PgVectorAdapter.capabilities() should be a dict containing at least the
    mandatory keys documented in BaseAdapter (here we check just 'filter').
    """
    db = await connect(dsn=dsn, min_pool_size=min_pool_size, max_pool_size=max_pool_size)
    caps = db.capabilities()

    assert isinstance(caps, dict), "capabilities() must return a dict"
    assert "filter" in caps, "capabilities() missing 'filter' key"
    assert isinstance(caps["filter"], bool), "'filter' value should be bool"

    await db.close()


async def test_connect_smoke(pgvector_config: tuple[str, int, int]):
    dsn, min_pool_size, max_pool_size = pgvector_config
    """
    Simple connection test: make sure the asyncpg pool is created
    when no explicit connection kwargs are provided (adapter reads
    PGV_* env vars set by the fixture).
    """
    db = await connect(
        dsn=dsn, min_pool_size=min_pool_size, max_pool_size=max_pool_size
    )  # <- no dsn/host/port
    assert db.pool is not None  # pool object exists
    await db.close()
