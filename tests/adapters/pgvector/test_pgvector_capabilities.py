from __future__ import annotations
import pytest, vverb

pytestmark = pytest.mark.asyncio


async def test_capabilities_structure(pgvector_container: str):
    """
    PgVectorAdapter.capabilities() should be a dict containing at least the
    mandatory keys documented in BaseAdapter (here we check just 'filter').
    """
    db = await vverb.connect("pgvector", dsn=pgvector_container)
    caps = db.capabilities()

    assert isinstance(caps, dict), "capabilities() must return a dict"
    assert "filter" in caps, "capabilities() missing 'filter' key"
    assert isinstance(caps["filter"], bool), "'filter' value should be bool"

    await db.close()