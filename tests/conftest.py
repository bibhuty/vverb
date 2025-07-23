# tests/conftest.py
from __future__ import annotations
import asyncio, os, subprocess, time, pathlib
import pytest, pytest_asyncio
import asyncpg
from pgvector.asyncpg import register_vector

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------
CONTAINER_NAME = "pgvector-test"
HOST_PORT      = "6263"                 # host → container 5432
IMAGE_TAG      = "pgvector/pgvector:0.8.0-pg17"
DSN_TEMPLATE   = "postgresql://pgvector:pgvector@localhost:{port}/vverb"

INIT_SQL_PATH  = pathlib.Path(__file__).parent.parent / "init-vector.sql"
if not INIT_SQL_PATH.exists():
    raise FileNotFoundError("Create init-vector.sql in repo root first!")

def _run_cmd(*args: str):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

# ---------------------------------------------------------------------------
# 1.  Session-wide pgvector container
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def pgvector_container() -> str:
    """
    Spin up pgvector once per pytest session.  Yields the ready DSN
    (postgresql://user:pass@localhost:6263/vverb).  Tears container down
    at the end of the session.
    """
    # Remove any stale container quietly
    subprocess.run(["docker", "rm", "-f", CONTAINER_NAME],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    _run_cmd(
        "docker", "run", "--name", CONTAINER_NAME,
        "-e", "POSTGRES_USER=pgvector",
        "-e", "POSTGRES_PASSWORD=pgvector",
        "-e", "POSTGRES_DB=vverb",
        "-v", f"{INIT_SQL_PATH}:/docker-entrypoint-initdb.d/init-vector.sql:ro",
        "-p", f"{HOST_PORT}:5432",
        "-d", IMAGE_TAG
    )

    # Wait a few seconds for Postgres to accept connections
    time.sleep(5)

    dsn = DSN_TEMPLATE.format(port=HOST_PORT)
    yield dsn

    # Teardown
    _run_cmd("docker", "rm", "-f", CONTAINER_NAME)

# ---------------------------------------------------------------------------
# 2.  Per-test asyncpg connection (clean slate each time)
# ---------------------------------------------------------------------------
@pytest_asyncio.fixture(scope="function")
async def conn(pgvector_container: str):
    """
    Asyncpg connection fixture — registers pgvector type codec,
    creates a demo table once per test, truncates afterwards.
    """
    dsn  = pgvector_container
    conn = await asyncpg.connect(dsn)
    await register_vector(conn)

    await conn.execute("""
        CREATE TABLE IF NOT EXISTS items (
          id        text PRIMARY KEY,
          embedding vector(3)
        );
    """)

    yield conn                                           # <── test runs here

    await conn.execute("TRUNCATE items;")
    await conn.close()

# ---------------------------------------------------------------------------
# 3.  pytest-asyncio event-loop override (one loop per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()