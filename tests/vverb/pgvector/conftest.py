# tests/vverb/pgvector/conftest.py
from __future__ import annotations

import asyncio
import os
import pathlib
import subprocess
import time
from typing import Any, Generator

import asyncpg
import pytest
import pytest_asyncio
from pgvector.asyncpg import register_vector

# ───────────────────────────────────────────────────────────────
# ENV-BACKED CONSTANTS (with defaults)
# ───────────────────────────────────────────────────────────────
PGV_HOST = os.getenv("PGV_HOST", "localhost")
PGV_PORT = os.getenv("PGV_PORT", "6263")
PGV_DB = os.getenv("PGV_DB", "vverb")
PGV_USER = os.getenv("PGV_USER", "pgvector")
PGV_PASS = os.getenv("PGV_PASS", "pgvector")
PGV_MIN_SIZE = os.getenv("PGV_MIN_SIZE", "1")
PGV_MAX_SIZE = os.getenv("PGV_MAX_SIZE", "10")

# ───────────────────────────────────────────────────────────────
# Docker Compose config: Use correct relative path
# ───────────────────────────────────────────────────────────────
DOCKER_COMPOSE_FILE = os.getenv(
    "PGV_DOCKER_COMPOSE",
    str(
        (
            pathlib.Path(__file__).resolve().parent.parent.parent.parent
            / "docker"
            / "test"
            / "docker-compose.pgvector-test.yaml"
        )
    ),
)
CONTAINER_NAME = os.getenv("PGV_CONTAINER_NAME", "pgvector-test")


def _run_cmd(*args: str):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


# ───────────────────────────────────────────────────────────────
# 1. Session-wide pgvector container via docker-compose
# ───────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def pgvector_config() -> Generator[tuple[str, str, str], Any, None]:
    """
    Starts a pgvector container once per session using docker-compose,
    yields the DSN, and tears down when tests complete.
    """
    # Tear down any previous container (ignore errors)
    subprocess.run(
        ["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "down", "-v"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Launch via docker-compose
    _run_cmd("docker", "compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d")

    # Wait for Postgres to be ready
    for _ in range(15):
        try:
            conn = asyncio.run(
                asyncpg.connect(
                    host=PGV_HOST,
                    port=int(PGV_PORT),
                    user=PGV_USER,
                    password=PGV_PASS,
                    database=PGV_DB,
                )
            )
            conn.close()
            break
        except Exception:
            time.sleep(1)
    else:
        raise RuntimeError("pgvector test database did not start in time.")

    dsn = f"postgresql://{PGV_USER}:{PGV_PASS}@{PGV_HOST}:{PGV_PORT}/{PGV_DB}"
    min_pool_size = PGV_MIN_SIZE
    max_pool_size = PGV_MAX_SIZE

    yield dsn, min_pool_size, max_pool_size

    # Teardown
    _run_cmd("docker", "compose", "-f", DOCKER_COMPOSE_FILE, "down", "-v")


# ───────────────────────────────────────────────────────────────
# 2. Per-test asyncpg connection (clean slate each time)
# ───────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def conn(pgvector_config: tuple[str, int, int]):
    dsn = pgvector_config[0]
    """
    Asyncpg connection fixture with pgvector type registered.
    Creates a fresh `items` table each test.
    """
    conn = await asyncpg.connect(dsn)
    await register_vector(conn)

    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
          id        text PRIMARY KEY,
          embedding vector(3)
        );
        """
    )
    await conn.execute(
        """
        CREATE EXTENSION IF NOT EXISTS vector;
    """
    )
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
