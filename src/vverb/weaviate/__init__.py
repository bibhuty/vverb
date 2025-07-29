"""
vverb.weaviate – public API surface for the Weaviate adapter.
"""

from .core import WeaviateAdapter

# Convenience entry-point so callers can simply:
# from vverb.weaviate import connect

connect = WeaviateAdapter.connect

__all__: list[str] = ["connect", "WeaviateAdapter"]