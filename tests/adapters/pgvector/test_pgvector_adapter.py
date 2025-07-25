# tests/adapters/pgvector/test_pgvector_adapter.py
from __future__ import annotations

import pytest
import pytest_asyncio

import vverb

pytestmark = pytest.mark.asyncio


# ───────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────
@pytest_asyncio.fixture
async def db(pgvector_config: tuple[str, int, int]):
    dsn, min_pool_size, max_pool_size = pgvector_config
    """Connected PgVectorAdapter instance."""
    database = await vverb.connect("pgvector", dsn=dsn, min_pool_size=min_pool_size, max_pool_size=max_pool_size)
    try:
        yield database
    finally:
        await database.close()

async def test_create_extension(db):
    """
    Ensure the pgvector extension is created if it doesn't exist.
    This is a no-op if the extension is already installed.
    """
    await db._ensure_vector_extension()

    # Verify by checking if the extension exists
    async with db.raw() as conn:
        result = await conn.fetchval("SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector';")
        assert result == 1, "pgvector extension should be installed"