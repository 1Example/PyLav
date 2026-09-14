from __future__ import annotations

import contextlib
import socket

import aiohttp
from cashews import Cache  # type: ignore
from yarl import URL

from pylav.compat import json
from pylav.exceptions.base import PyLavException
from pylav.logging import getLogger

LOGGER = getLogger("PyLav.extension.RadioBrowser")


CACHE = Cache("RADIO")
CACHE.setup("mem://?check_interval=10", size=1_000_000, enable=True)


class Error(PyLavException):
    """Base class for all exceptions raised by this module"""


class RDNSLookupError(Error):
    """Raised when there was a problem with performing reverse dns lookup for ip."""

    __slots__ = ("ip", "port")

    def __init__(self, ip: str) -> None:
        self.ip = ip
        self.error_msg = f"There was a problem with performing reverse dns lookup for ip: {ip}"
        super().__init__(self.error_msg)


@CACHE(ttl=3600, prefix="fetch_servers")
async def fetch_servers() -> set[str]:
    """
    Get IP of all currently available `Radio Browser` servers.
    Returns:
        set: List of addresses.
    """
    try:
        async with aiohttp.ClientSession(json_serialize=json.dumps) as session:
            async with session.get("http://all.api.radio-browser.info/json/servers") as response:
                data = await response.json(loads=json.loads)
    except socket.gaierror:
        return set()
    else:
        return {server["name"] for server in data}


@CACHE(ttl=300, prefix="pick_base_url", key="chosen")
async def pick_base_url(session: aiohttp.ClientSession) -> URL | None:
    """Pick a base url for the RadioBrowser API."""
    servers = await fetch_servers()
    if not servers:
        LOGGER.warning("RadioBrowser API seems to be down at the moment, disabling Radio functionality.")
        return None
    for host in servers:
        with contextlib.suppress(Exception):
            async with session.get(f"https://{host}/json/stats") as response:
                if response.status == 200:
                    return URL(f"https://{host}")
                LOGGER.verbose("Error interacting with %s: %s", host, response.status)
    LOGGER.error("All the following hosts for the RadioBrowser API are broken: %s", ", ".join(servers))


async def invalidate_base_url() -> None:
    """Forget the currently cached mirror choice.

    pick_base_url() only re-checks which mirror is healthy once every 5
    minutes (its cache TTL above). If the mirror it handed out stops
    answering partway through that window - as opposed to being
    unreachable from the very start, which the health-check loop above
    already guards against - every request keeps hitting the same dead
    host until the cache naturally expires. Call this right after a
    request to the cached mirror fails so the next pick_base_url() call
    actually re-probes instead of returning the same stale choice.
    """
    await CACHE.delete("pick_base_url:chosen")
