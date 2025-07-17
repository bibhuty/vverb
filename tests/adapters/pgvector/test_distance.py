# tests/backend/adapters/pgvector/test_distance.py
import pytest

@pytest.mark.asyncio
async def test_jaccard_distance(conn):
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS items(
            id text PRIMARY KEY,
            embedding vector(3)
        );
        CREATE EXTENSION IF NOT EXISTS vector;  -- idempotent
    """)
    await conn.executemany(
        "INSERT INTO items(id, embedding) VALUES($1, $2)",
        [("a",[1,0,0]), ("b",[1,1,0]), ("c",[0,1,1])]
    )
    rows = await conn.fetch(
      "SELECT id, embedding <#> $1 AS dist FROM items ORDER BY dist",
      [1,0,0]                  # Jaccard operator <#>
    )
    assert [r["id"] for r in rows] == ["a","b","c"]