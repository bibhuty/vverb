from __future__ import annotations
import uuid, pytest

import pytest_asyncio

import vverb
from vverb.util.schema import TableSchema, VectorCol, FieldCol, FieldType, Metric

pytestmark = pytest.mark.asyncio

@pytest_asyncio.fixture
async def db(pgvector_config: tuple[str,int,int]):
    dsn, min_pool_size, max_pool_size = pgvector_config
    """Connected PgVectorAdapter instance."""
    database = await vverb.connect("pgvector", dsn=dsn, min_pool_size=min_pool_size, max_pool_size=max_pool_size)
    try:
        yield database
    finally:
        await database.close()

async def test_create_table(db):
    """
    Ensure PgVectorAdapter.create_collection actually creates
    the table with correct vector column and index.
    """
    table_name = "vv_" + uuid.uuid4().hex[:8]

    schema = TableSchema(
        table=table_name,
        vector=VectorCol("embedding", dim=3, metric=Metric.COSINE),
        fields=[FieldCol("title", FieldType.STRING)]
    )

    # 1) create
    await db.create_collection(schema)

    # 2) verify via catalog queries
    async with db.raw() as con:
        # table exists?
        tbl_count = await con.fetchval(
            "SELECT count(*) FROM pg_tables WHERE tablename = $1;", table_name
        )
        assert tbl_count == 1

        # vector column exists?
        col_count = await con.fetchval(
            """
            SELECT count(*) FROM information_schema.columns
             WHERE table_name = $1 AND column_name = 'embedding';
            """,
            table_name,
        )
        assert col_count == 1

        # index exists on vector column?
        idx_count = await con.fetchval(
            """
            SELECT count(*)
              FROM pg_indexes
             WHERE tablename = $1
               AND indexdef ILIKE '%' || $1 || '_embedding_idx%';
            """,
            table_name,
        )
        assert idx_count == 1

    # 3) drop table (cleanup) so next test run starts clean
    async with db.raw() as con:
        await con.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE;")