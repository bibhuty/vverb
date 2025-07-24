from ...util.schema import FieldType, Metric
from typing import Mapping

TYPE_MAP: Mapping[FieldType, str] = {
    FieldType.STRING:  "TEXT",
    FieldType.INT:     "INTEGER",
    FieldType.BIGINT:  "BIGINT",
    FieldType.FLOAT:   "REAL",
    FieldType.DOUBLE:  "DOUBLE PRECISION",
    FieldType.BOOLEAN: "BOOLEAN",
    FieldType.JSON:    "JSONB",
    FieldType.DATE:    "DATE",
    FieldType.UUID:    "UUID",
}

METRIC_OPCLASS: Mapping[Metric, str] = {
    Metric.COSINE:        "vector_cosine_ops",
    Metric.L2:            "vector_l2_ops",
    Metric.EUCLIDEAN:     "vector_l2_ops",
    Metric.INNER_PRODUCT: "vector_ip_ops",
    Metric.DOT:           "vector_ip_ops",
    Metric.DOT_PRODUCT:   "vector_ip_ops",
}