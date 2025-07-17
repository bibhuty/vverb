#!/usr/bin/env bash
set -e

echo "🔧  Creating backend-only skeleton …"

# Top-level files
echo -e "# vverb\n\nFive-verb wrapper for vector databases." > README.md
cat > pyproject.toml <<'PY'
[project]
name = "vverb"
version = "0.0.1"
description = "Five-verb wrapper for vector databases"
requires-python = ">=3.9"
dependencies = ["asyncpg", "httpx", "pytest"]
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
PY

# Source layout
mkdir -p src/{core,adapters/{pgvector,qdrant},util}
touch src/__init__.py

# Core verb stubs
for verb in connect create_collection upsert query delete; do
  cat > "src/core/${verb}.py" <<PY
async def ${verb}(*args, **kwargs):
    raise NotImplementedError("${verb} not implemented yet")
PY
done

# Adapter stubs
for engine in pgvector qdrant; do
  mkdir -p "src/adapters/${engine}"
  for verb in connect create_collection upsert query delete; do
    cat > "src/adapters/${engine}/${verb}.py" <<PY
async def ${verb}(*args, **kwargs):
    # TODO: implement ${verb} for ${engine}
    raise NotImplementedError("${engine}.${verb} pending")
PY
  done
done

# Tests layout
mkdir -p tests/backend/core
cat > tests/core/test_placeholder.py <<'TEST'
def test_placeholder():
    assert True
TEST

echo "✅  Backend skeleton ready."

#python -m venv .venv && source .venv/bin/activate
#pip install -e ".[dev]"       # editable install
#pytest -q                     # should show 1 passing test