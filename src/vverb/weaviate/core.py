# this file will connect to a Weaviate instance using object-oriented Python client.
"""
Weaviate adapter implementation for vverb.

Implements the five core verbs:
    • connect  • create_collection  • upsert  • query  • delete
plus capability negotiation.
"""

from __future__ import annotations
from typing import Any
from vverb._log import logger as _root_logger
from vverb.base import BaseAdapter  # vverb.adapters.base

import weaviate
from weaviate.connect import ConnectionParams
from weaviate import WeaviateAsyncClient
import os
import asyncio

log = _root_logger.getChild("weaviate")

__all__ = ["WeaviateAdapter"]

class WeaviateAdapter(BaseAdapter):
    """
    Concrete adapter for Weaviate.

    Parameters accepted by `connect`
    --------------------------------
    http_host : str             HTTP host, default "localhost"
    http_port : int             HTTP port, default 8080
    http_secure : bool          Use HTTPS, default False
    grpc_host : str             gRPC host, default "localhost"
    grpc_port : int             gRPC port, default 50052
    grpc_secure : bool          Use gRPC over TLS, default False
    min_pool_size : int        Pool min connections (default 1)
    max_pool_size : int        Pool max connections (default 5)
    """
    
    def __init__(self, client: WeaviateAsyncClient, **cfg: Any):
        self.client = client
        self.cfg = cfg  # keep original config for debugging

    @classmethod
    async def connect(
        cls,
        http_host: str = "localhost",
        http_port: int = 8080,
        http_secure: bool = False,
        grpc_host: str = "localhost",
        grpc_port: int = 50051,
        grpc_secure: bool = False,
        **cfg: Any
        ) -> WeaviateAdapter:
        """
        Create and connect a WeaviateAsyncClient instance.
        This method is used to instantiate the client with default parameters.
        Returns:
            WeaviateAsyncClient: Connected client instance.
        """
        client = weaviate.WeaviateAsyncClient(
            connection_params=ConnectionParams.from_params(
                http_host=http_host,
                http_port=http_port,
                http_secure=http_secure,
                grpc_host=grpc_host,
                grpc_port=grpc_port,
                grpc_secure=grpc_secure,
                ),
            )
        await client.connect()
        adaptor = cls(client, **cfg)
        await adaptor.client.is_ready() # Ensure the client is ready
        return adaptor

    def capabilities(self):
        pass

    async def close(self):
        await self.client.close()

    async def create_collection(self, name, schema):
        pass

    async def delete(self, collection_name, id):
        pass

    async def query(self, collection_name, filter=None):
        pass

    async def upsert(self, collection_name, data):
        pass


# For Temporary Test Purpose. Remove it in Future.
if __name__ == "__main__":
    # Example usage
    async def main():
        try:
            client = await WeaviateAdapter.connect(
                http_host="localhost",
                http_port=8080,
                http_secure=False,
                grpc_host="localhost",
                grpc_port=50051,
                grpc_secure=False
            )
            adapter = WeaviateAdapter(client)
            log.info("Weaviate client connected successfully.")
        finally:
            await adapter.close()
            log.info("Weaviate client closed.")

    asyncio.run(main())