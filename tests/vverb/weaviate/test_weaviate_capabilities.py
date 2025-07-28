from __future__ import annotations
import pytest

from vverb.weaviate import connect

@pytest.mark.asyncio
async def test_connection_smoke(weaviate_client):
    """
    Simple smoke test to verify Weaviate connection and basic health.
    """
    host, port = weaviate_client
    # Connect to Weaviate using the provided host and port
    client = await connect(http_host=host, http_port=int(port))
    assert client is not None