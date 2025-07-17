# tests/backend/adapters/pgvector/conftest.py
import asyncio, os, subprocess, time
import pytest
import asyncpg
import pytest_asyncio
from pgvector.asyncpg import register_vector

import pytest
pytestmark = pytest.mark.asyncio    # applies to every test in this dir

CONTAINER_NAME = "pgvector-test"
HOST_PORT      = "6263"          # host → container 5432
DSN_TEMPLATE   = "postgresql://pgvector:pgvector@localhost:{port}/vverb"


def _run_cmd(*args):
    """Run a shell command, capturing stderr for easier debug."""
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL)


@pytest.fixture(scope="session")
def pgvector_container():
    """
    Launch `pgvector/pgvector:0.8.0-pg17` once per pytest session and
    remove it (and its volume) afterwards.
    """
    init_sql = os.path.abspath("init-vector.sql")
    if not os.path.exists(init_sql):
        raise FileNotFoundError("init-vector.sql not found in repo root")

    # Remove any stale container
    subprocess.run(["docker", "rm", "-f", CONTAINER_NAME],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Start fresh
    _run_cmd(
        "docker", "run", "--name", CONTAINER_NAME,
        "-e", "POSTGRES_USER=pgvector",
        "-e", "POSTGRES_PASSWORD=pgvector",
        "-e", "POSTGRES_DB=vverb",
        "-v", f"{init_sql}:/docker-entrypoint-initdb.d/init-vector.sql:ro",
        "-p", f"{HOST_PORT}:5432", "-d",
        "pgvector/pgvector:0.8.0-pg17"
    )

    # Give Postgres a few seconds to become ready
    time.sleep(5)
    yield DSN_TEMPLATE.format(port=HOST_PORT)

    # Teardown: stop & remove
    _run_cmd("docker", "rm", "-f", CONTAINER_NAME)


@pytest_asyncio.fixture(scope="function")
async def conn(pgvector_container):
    """
    Asyncpg connection fixture (setup per test function, auto-cleans).
    """
    dsn = pgvector_container
    conn = await asyncpg.connect(dsn)
    await register_vector(conn)

    # Ensure test table is present (idempotent for quick demos)
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS items(
          id        text PRIMARY KEY,
          embedding vector(3)
        );
    """)

    yield conn

    # Clean slate after each test
    await conn.execute("TRUNCATE items;")
    await conn.close()