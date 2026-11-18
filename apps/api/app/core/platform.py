from __future__ import annotations

import asyncio
import platform


def psycopg_compatible_loop_factory() -> asyncio.AbstractEventLoop:
    """Create an event loop supported by async psycopg on every platform."""

    if platform.system() == "Windows":
        return asyncio.SelectorEventLoop()
    return asyncio.new_event_loop()
