# conftest.py for Weaviate adapter tests
from __future__ import annotations

import asyncio
import os
import pathlib
import subprocess
import time
from typing import Any, Generator

import pytest
import pytest_asyncio

# ───────────────────────────────────────────────────────────────
# ENV-BACKED CONSTANTS (with defaults)
# ───────────────────────────────────────────────────────────────

WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT = os.getenv("WEAVIATE_PORT", "8080")
DOCKER_COMPOSE_PATH = pathlib.Path(__file__).parent / "docker-compose.yml"

# ───────────────────────────────────────────────────────────────
# Helper to run shell commands
# ───────────────────────────────────────────────────────────────

def _run_cmd(*args: str):
    """Run a shell command, suppressing output and raising on error."""
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# ───────────────────────────────────────────────────────────────
# 1. Session-wide Weaviate container via docker-compose
# ───────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def weaviate_config() -> Generator[tuple[str, str], Any, None]:
    """
    Starts a Weaviate container using docker-compose once per session, then:
    - Yields the host and port for connection
    - Tears it down when tests complete
    """
    # Ensure no stale container
    _run_cmd("docker-compose" ,"-f" , str(DOCKER_COMPOSE_PATH), "down")

    # Launch fresh container
    _run_cmd("docker-compose", "-f", str(DOCKER_COMPOSE_PATH), "up", "-d")

    # Wait for Weaviate to be ready
    time.sleep(10)  # Increase if needed for slow startup

    # Build connection info
    host = WEAVIATE_HOST
    port = WEAVIATE_PORT

    yield host, port

    # Teardown containers
    _run_cmd("docker-compose", "-f", str(DOCKER_COMPOSE_PATH), "down")

# ───────────────────────────────────────────────────────────────
# 2. Per-test async connection (stub, to be replaced with actual client)
# ───────────────────────────────────────────────────────────────
@pytest_asyncio.fixture(scope="function")
async def weaviate_client(weaviate_config: tuple[str, str]):
    """
    Example async fixture for connecting to Weaviate.
    """
    host, port = weaviate_config
    # Return the host and port for use in tests
    yield host, port

# ───────────────────────────────────────────────────────────────
# 3. Single event loop for pytest-asyncio
# ───────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for all async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()