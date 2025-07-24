"""
Cross-engine schema primitives.

* Metric – all similarity functions exposed by pgvector, Qdrant, Milvus,
           Weaviate and Pinecone today.
* FieldType – common scalar types you can safely map across DBs; each adapter
              converts to its native name (e.g., 'float' → FLOAT / DOUBLE /
              float8).

You can always extend these enums later without breaking callers:
    >>> Metric.HAMMING  # added in the future
"""

from __future__ import annotations
from enum import Enum
from typing import Literal, Dict, Any, Sequence
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Similarity metrics (vector space distance) ────────────────────────────────
# ---------------------------------------------------------------------------

class Metric(str, Enum):
    COSINE         = "cosine"         # pgvector / Qdrant / Milvus / Weaviate / Pinecone
    EUCLIDEAN      = "euclidean"      # Pinecone keyword
    L2             = "l2"             # pgvector / Milvus (same as Euclidean)
    DOT            = "dot"            # Weaviate
    DOT_PRODUCT    = "dotproduct"     # Pinecone
    INNER_PRODUCT  = "ip"             # pgvector / Milvus
    HAMMING        = "hamming"        # Milvus (binary)
    JACCARD        = "jaccard"        # Milvus (binary)
    TANIMOTO       = "tanimoto"       # Milvus (binary)
    # add more later as Literal str Enum values


# ---------------------------------------------------------------------------
# Scalar field types  ───────────────────────────────────────────────────────
# ---------------------------------------------------------------------------

class FieldType(str, Enum):
    STRING   = "string"   # VARCHAR, TEXT, keyword, etc.
    INT      = "int"      # 32-bit signed
    BIGINT   = "bigint"   # 64-bit signed
    FLOAT    = "float"    # 32-bit
    DOUBLE   = "double"   # 64-bit
    BOOLEAN  = "bool"
    JSON     = "json"
    DATE     = "date"
    UUID     = "uuid"
    # extend with "binary", "int8", "int16", etc. when an adapter needs it


# ---------------------------------------------------------------------------
# Dataclasses for high-level schema description
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class VectorCol:
    name: str
    dim: int
    metric: Metric = Metric.COSINE


@dataclass(slots=True)
class FieldCol:
    name: str
    ftype: FieldType
    not_null: bool = False
    default: str | None = None
    extras: Dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TableSchema:
    table: str
    vector: VectorCol
    fields: Sequence[FieldCol] = field(default_factory=list)
    id_field: str = "id"