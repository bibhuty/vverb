# tests/conftest.py
from __future__ import annotations
import asyncio, os, subprocess, time, pathlib
from typing import Any, Generator

import pytest, pytest_asyncio
import asyncpg
from pgvector.asyncpg import register_vector

# ───────────────────────────────────────────────────────────────
# ENV-BACKED CONSTANTS (with defaults)
# ───────────────────────────────────────────────────────────────
PGV_HOST     = os.getenv("PGV_HOST", "localhost")
PGV_PORT     = os.getenv("PGV_PORT", "6263")
PGV_DB       = os.getenv("PGV_DB", "vverb")
PGV_USER     = os.getenv("PGV_USER", "pgvector")
PGV_PASS     = os.getenv("PGV_PASS", "pgvector")
PGV_MIN_SIZE = os.getenv("PGV_MIN_SIZE", "1")
PGV_MAX_SIZE = os.getenv("PGV_MAX_SIZE", "10")

# ───────────────────────────────────────────────────────────────
# Docker & DSN constants
# ───────────────────────────────────────────────────────────────
CONTAINER_NAME = os.getenv("PGV_CONTAINER_NAME", "pgvector-test")
IMAGE_TAG      = os.getenv("PGV_IMAGE_TAG", "pgvector/pgvector:0.8.0-pg17")

INIT_SQL_PATH = pathlib.Path(__file__).parent / "init-vector.sql"
if not INIT_SQL_PATH.exists():
    raise FileNotFoundError("Create init-vector.sql in tests/adapters/pgvector first!")

def _run_cmd(*args: str):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ───────────────────────────────────────────────────────────────
# 1. Session-wide pgvector container
# ───────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def pgvector_config() -> Generator[tuple[str, str, str], Any, None]:
    """
    Starts a pgvector container once per session, then:
    - Yields the DSN
    - Tears it down when tests complete
    """
    # Ensure no stale container
    subprocess.run(["docker", "rm", "-f", CONTAINER_NAME],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Launch fresh
    _run_cmd(
        "docker", "run", "--name", CONTAINER_NAME,
        "-e", f"POSTGRES_USER={PGV_USER}",
        "-e", f"POSTGRES_PASSWORD={PGV_PASS}",
        "-e", f"POSTGRES_DB={PGV_DB}",
        "-v", f"{INIT_SQL_PATH}:/docker-entrypoint-initdb.d/init-vector.sql:ro",
        "-p", f"{PGV_PORT}:5432",
        "-d", IMAGE_TAG
    )

    # Wait for Postgres to be ready
    time.sleep(5)

    # Build DSN pointing at our container
    dsn = f"postgresql://{PGV_USER}:{PGV_PASS}@{PGV_HOST}:{PGV_PORT}/{PGV_DB}"
    min_pool_size = PGV_MIN_SIZE
    max_pool_size = PGV_MAX_SIZE

    yield dsn, min_pool_size, max_pool_size

    # Teardown
    _run_cmd("docker", "rm", "-f", CONTAINER_NAME)

# ───────────────────────────────────────────────────────────────
# 2. Per-test asyncpg connection (clean slate each time)
# ───────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def conn(pgvector_config: tuple[str,int,int]):
    dsn = pgvector_config[0]
    """
    Asyncpg connection fixture with pgvector type registered.
    Creates a fresh `items` table each test.
    """
    conn = await asyncpg.connect(dsn)
    await register_vector(conn)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
          id        text PRIMARY KEY,
          embedding vector(3)
        );
    """)

    yield conn

    await conn.execute("TRUNCATE items;")
    await conn.close()

# ───────────────────────────────────────────────────────────────
# 3. Single event loop for pytest-asyncio
# ───────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()