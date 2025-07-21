# vverb

Five-verb wrapper for vector databases.
### Initial adapter set (v1.0)

| # | Engine         | Notes                                             |
|---|----------------|---------------------------------------------------|
| 1 | **pgvector**   | PostgreSQL extension – easiest local start        |
| 2 | **Qdrant**     | OSS / Rust – hybrid filter, REST + gRPC           |
| 3 | **Milvus 2.x** | OSS / C++ – large-scale, HNSW + IVF + DiskANN     |
| 4 | **Weaviate**   | OSS / SaaS – native BM25 + vector, GraphQL & REST |
| 5 | **Pinecone**   | Fully managed SaaS baseline                       |