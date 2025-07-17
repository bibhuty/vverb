# tests/backend/adapters/pgvector/test_upsert_query.py
import pytest

@pytest.mark.asyncio
async def test_upsert_and_query(conn):
    await conn.execute(
        "INSERT INTO items (id, embedding) VALUES ($1, $2)",
        "a", [0.1, 0.2, 0.3]
    )

    rows = await conn.fetch(
        "SELECT id FROM items ORDER BY embedding <-> $1 LIMIT 1",
        [0.1, 0.2, 0.3]
    )
    assert rows[0]["id"] == "a"