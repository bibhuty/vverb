# tests/conftest.py
from __future__ import annotations
import asyncio, os, subprocess, time, pathlib
import pytest, pytest_asyncio
import asyncpg
from pgvector.asyncpg import register_vector

# ───────────────────────────────────────────────────────────────
# CONSTANTS
# ───────────────────────────────────────────────────────────────
CONTAINER_NAME = "pgvector-test"
HOST_PORT      = "6263"                 # host → container 5432
IMAGE_TAG      = "pgvector/pgvector:0.8.0-pg17"
DSN_TEMPLATE   = "postgresql://pgvector:pgvector@localhost:{port}/vverb"

INIT_SQL_PATH  = pathlib.Path(__file__).parent / "init-vector.sql"
if not INIT_SQL_PATH.exists():
    raise FileNotFoundError("Create init-vector.sql in repo root first!")

def _run_cmd(*args: str):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)

# ───────────────────────────────────────────────────────────────
# 1. Session-wide pgvector container
# ───────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def pgvector_container() -> str:
    """
    Start pgvector once per test session, export env vars so adapter
    can connect with zero kwargs, yield the DSN, then tear down.
    """
    # Clean any stale container
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

    time.sleep(5)  # allow Postgres to accept connections

    dsn = DSN_TEMPLATE.format(port=HOST_PORT)

    # ---------- export env vars for PgVectorAdapter ----------
    os.environ["PGV_DSN"]  = dsn
    os.environ["PGV_HOST"] = "localhost"
    os.environ["PGV_PORT"] = HOST_PORT
    os.environ["PGV_DB"]   = "vverb"
    os.environ["PGV_USER"] = "pgvector"
    os.environ["PGV_PASS"] = "pgvector"
    os.environ["PGV_MIN_SIZE"] = "1"
    os.environ["PGV_MAX_SIZE"] = "10"
    # ---------------------------------------------------------

    yield dsn

    _run_cmd("docker", "rm", "-f", CONTAINER_NAME)

# ───────────────────────────────────────────────────────────────
# 2. Per-test asyncpg connection (clean slate each time)
# ───────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def conn(pgvector_container: str):
    """Asyncpg connection fixture with pgvector type registered."""
    conn = await asyncpg.connect(pgvector_container)
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