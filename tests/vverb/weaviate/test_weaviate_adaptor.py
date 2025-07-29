from __future__ import annotations

import pytest
import pytest_asyncio

# Import the adapter's connect function
from vverb.weaviate import connect

pytestmark = pytest.mark.asyncio

# ───────────────────────────────────────────────
# Fixtures
# ───────────────────────────────────────────────

@pytest_asyncio.fixture
async def db(weaviate_config: tuple[str, str]):
    """Yield a connected WeaviateAdapter instance."""
    host, port = weaviate_config

    database = await connect(
        http_host=host,
        http_port=int(port),
        http_secure=False,  # Set True if your setup uses HTTPS
        grpc_host=host,
        grpc_port=50051,    # Adjust if needed
        grpc_secure=False
    )
    try:
        yield database
    finally:
        await database.close()

# ───────────────────────────────────────────────
# Tests
# ───────────────────────────────────────────────

async def test_is_ready(db):
    """
    Ensure the Weaviate client is ready and healthy.
    """
    is_ready = await db.client.is_ready()
    assert is_ready is True, "Weaviate client should be ready"