"""
vverb.pgvector – public API surface for the PGVector adapter.
"""

from .core import PgVectorAdapter

# Convenience entry-point so callers can simply:
#     from vverb.pgvector import connect
connect = PgVectorAdapter.connect

__all__: list[str] = ["connect", "PgVectorAdapter"]
