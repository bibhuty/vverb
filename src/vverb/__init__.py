"""
Public entry-point for vverb.

Example
-------
    import vverb
    db = await vverb.connect("pgvector", dsn="postgres://...")
"""

from importlib import import_module
from typing import Any

_ADAPTERS = {
    "pgvector":  ("vverb.adapters.pgvector.core", "PgVectorAdapter"),
    # qdrant, milvus, … will be added later
}

async def connect(backend: str, **cfg: Any):
    """
    Factory that imports the requested adapter on-demand
    and returns a connected instance.

    Parameters
    ----------
    backend : str
        One of: "pgvector", "qdrant", "milvus", "weaviate", "pinecone".
    **cfg
        Keyword arguments passed straight to `<Adapter>.connect(**cfg)`.
    """
    backend = backend.lower()
    try:
        module_name, cls_name = _ADAPTERS[backend]
    except KeyError:
        raise ValueError(f"Unknown backend '{backend}'. "
                         f"Supported: {', '.join(_ADAPTERS)}")

    module = import_module(module_name)
    AdapterClass = getattr(module, cls_name)          # type: ignore[attr-defined]
    return await AdapterClass.connect(**cfg)          # noqa: E1102