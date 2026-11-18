from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping

import pytest

from app.core.platform import psycopg_compatible_loop_factory


def pytest_asyncio_loop_factories(
    config: pytest.Config,
    item: pytest.Item,
) -> Mapping[str, Callable[[], asyncio.AbstractEventLoop]]:
    """Use a psycopg-compatible loop on every test platform."""

    return {"psycopg-compatible": psycopg_compatible_loop_factory}
