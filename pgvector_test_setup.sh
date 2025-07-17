#!/usr/bin/env bash
docker pull pgvector/pgvector:0.8.0-pg17
echo "CREATE EXTENSION IF NOT EXISTS vector;" > init-vector.sql
docker run --name pgvector-test \
  -e POSTGRES_USER=pgvector \
  -e POSTGRES_PASSWORD=pgvector \
  -e POSTGRES_DB=vverb \
  -v "$PWD/init-vector.sql":/docker-entrypoint-initdb.d/init-vector.sql:ro \
  -p 6263:5432 \
  -d pgvector/pgvector:0.8.0-pg17