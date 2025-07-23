# tests/adapters/pgvector/test_pgvector_adapter.py
from __future__ import annotations
import uuid, pytest, pytest_asyncio
import vverb

pytestmark = pytest.mark.asyncio


# ───────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────
@pytest_asyncio.fixture
async def db(pgvector_container: str):
    """Connected PgVectorAdapter instance."""
    adapter = await vverb.connect("pgvector", dsn=pgvector_container)
    try:
        yield adapter
    finally:
        await adapter.close()


@pytest_asyncio.fixture
def coll_name():
    """Unique table / collection name per test."""
    return "vv_" + uuid.uuid4().hex[:8]


V1, V2, V3 = [1.0, 0, 0], [0, 1.0, 0], [0, 0, 1.0]


# ───────────────────────────────────────────────
# Tests (currently marked xfail)
# ───────────────────────────────────────────────
@pytest.mark.xfail(reason="PgVectorAdapter verbs not implemented yet", strict=False)
async def test_lifecycle_roundtrip(db, coll_name):
    await db.create_collection(coll_name, dim=3, metric="cosine", skip_if_exists=True)
    await db.upsert(coll_name, ["x", "y"], [V1, V2])

    hits = await db.query(coll_name, V1, k=2)
    ids = [h["id"] for h in hits]
    assert ids[0] == "x" and set(ids) == {"x", "y"}

    await db.delete(coll_name, ["x"])
    hits_after = await db.query(coll_name, V1, k=2)
    assert all(h["id"] != "x" for h in hits_after)


@pytest.mark.xfail(reason="PgVectorAdapter verbs not implemented yet", strict=False)
async def test_conflict_update_vs_ignore(db, coll_name):
    await db.create_collection(coll_name, dim=3, metric="cosine", skip_if_exists=True)
    await db.upsert(coll_name, ["a"], [V1])

    # overwrite
    await db.upsert(coll_name, ["a"], [V3], if_exists="update")
    hit = (await db.query(coll_name, V3, k=1))[0]
    assert hit["id"] == "a" and hit["score"] > 0.99

    # attempt overwrite but ignore
    await db.upsert(coll_name, ["a"], [V1], if_exists="ignore")
    hit2 = (await db.query(coll_name, V3, k=1))[0]
    assert hit2["score"] > 0.99