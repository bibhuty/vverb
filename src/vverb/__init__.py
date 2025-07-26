"""
vverb namespace package.

Usage
-----
Pick the adapter you need and import it explicitly:

    from vverb.pgvector import connect
    db = await connect(dsn="postgres://...")

Each adapter lives in its own sub-package under ``vverb.<adapter>``.
No central ``vverb.connect()`` helper is provided anymore.
"""

# Nothing else on purpose: keep the root package clean.
__all__: list[str] = []
