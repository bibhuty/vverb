# tests/adapters/pgvector/test_pgvector_adapter.py
from __future__ import annotations
import uuid, pytest, pytest_asyncio
import vverb
from vverb.util.schema import TableSchema, VectorCol, FieldCol, FieldType, Metric

pytestmark = pytest.mark.asyncio


# ───────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────
@pytest_asyncio.fixture
async def db(pgvector_container: str):
    """Connected PgVectorAdapter instance."""
    database = await vverb.connect("pgvector", dsn=pgvector_container)
    try:
        yield database
    finally:
        await database.close()


@pytest_asyncio.fixture
def coll_name():
    """Unique table / collection name per test."""
    return "vv_" + uuid.uuid4().hex[:8]

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