from __future__ import annotations

import datetime
from dataclasses import dataclass, fields
from typing import TYPE_CHECKING, Any, TypeVar

from iso8601 import iso8601

from pylav.logging import getLogger
from pylav.players.query.obj import Query

if TYPE_CHECKING:
    from pylav.extension.radio.radios import RadioBrowser

LOGGER = getLogger("PyLav.extension.RadioBrowser")

T = TypeVar("T")
_WARNED: set[str] = set()


def build(cls: type[T], payload: dict[str, Any], **extra: Any) -> T:
    """Build one object from an API payload, ignoring fields we do not know.

    Radio Browser adds fields to its responses without warning, and these are
    plain dataclasses: passing one an unexpected keyword is a TypeError. That
    is how `geo_distance` appearing on stations took the whole extension down -
    every station fetch raised, and initialize() caught it, logged one vague
    line and switched the extension off for the session.

    An unknown field is not a reason to lose radio. It is logged once per
    field so it can be added deliberately, and dropped.
    """
    known = {f.name for f in fields(cls)}
    if unknown := payload.keys() - known:
        for name in sorted(unknown):
            key = f"{cls.__name__}.{name}"
            if key not in _WARNED:
                _WARNED.add(key)
                LOGGER.debug("%s sends %r, which PyLav does not use", cls.__name__, name)
    return cls(**extra, **{k: v for k, v in payload.items() if k in known})


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True)
class Station:
    """A station from the RadioBrowser API."""

    radio_api_client: RadioBrowser
    changeuuid: str | None = None
    stationuuid: str | None = None
    serveruuid: str | None = None
    name: str | None = None
    url: str | None = None
    url_resolved: str | None = None
    homepage: str | None = None
    favicon: str | None = None
    tags: str | None = None
    country: str | None = None
    countrycode: str | None = None
    iso_3166_2: str | None = None
    state: str | None = None
    language: str | None = None
    languagecodes: str | None = None
    votes: int | None = None
    lastchangetime: str | None = None
    lastchangetime_iso8601: str | datetime.datetime | None = None
    codec: str | None = None
    bitrate: int | None = None
    hls: int | None = None
    lastcheckok: int | None = None
    lastchecktime: str | None = None
    lastchecktime_iso8601: str | datetime.datetime | None = None
    lastcheckoktime: str | None = None
    lastcheckoktime_iso8601: str | datetime.datetime | None = None
    lastlocalchecktime: str | None = None
    lastlocalchecktime_iso8601: str | datetime.datetime | None = None
    clicktimestamp: str | None = None
    clicktimestamp_iso8601: str | datetime.datetime | None = None
    clickcount: int | None = None
    clicktrend: int | None = None
    ssl_error: int | None = None
    geo_lat: float | None = None
    geo_long: float | None = None
    geo_distance: float | None = None
    has_extended_info: int | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "ΩM4L42rPHqy123PyLavInvalidFallback-un5Nht475B"
        if isinstance(self.lastchangetime_iso8601, str):
            self.lastchangetime_iso8601 = iso8601.parse_date(self.lastchangetime_iso8601)
        if isinstance(self.lastchecktime_iso8601, str):
            self.lastchecktime_iso8601 = iso8601.parse_date(self.lastchecktime_iso8601)
        if isinstance(self.lastcheckoktime_iso8601, str):
            self.lastcheckoktime_iso8601 = iso8601.parse_date(self.lastcheckoktime_iso8601)
        if isinstance(self.lastlocalchecktime_iso8601, str):
            self.lastlocalchecktime_iso8601 = iso8601.parse_date(self.lastlocalchecktime_iso8601)
        if isinstance(self.clicktimestamp_iso8601, str):
            self.clicktimestamp_iso8601 = iso8601.parse_date(self.clicktimestamp_iso8601)

    async def get_query(self) -> Query:
        return await Query.from_string(self.url_resolved or self.url)

    async def click(self) -> None:
        """Increase the click count of a station by one.

        This should be called everytime when a user starts playing a stream to mark the stream more popular than others.
        Every call to this endpoint from the same IP address and for the same station only gets counted once per day.
        """
        await self.radio_api_client.click(station=self)


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True)
class Tag:
    """A tag from the RadioBrowser API."""

    name: str | None = None
    stationcount: int | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "ΩM4L42rPHqy123PyLavInvalidFallback-un5Nht475B"


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True)
class Language:
    """A language from the RadioBrowser API."""

    name: str | None = None
    iso_639: str | None = None
    stationcount: int | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "ΩM4L42rPHqy123PyLavInvalidFallback-un5Nht475B"


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True)
class State:
    """A state from the RadioBrowser API."""

    name: str | None = None
    country: str | None = None
    stationcount: int | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "ΩM4L42rPHqy123PyLavInvalidFallback-un5Nht475B"


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True)
class Codec:
    """A codec from the RadioBrowser API."""

    name: str | None = None
    stationcount: int | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "ΩM4L42rPHqy123PyLavInvalidFallback-un5Nht475B"


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True)
class CountryCode:
    """A country code from the RadioBrowser API."""

    name: str | None = None
    stationcount: int | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "ΩM4L42rPHqy123PyLavInvalidFallback-un5Nht475B"


@dataclass(eq=True, slots=True, unsafe_hash=True, order=True, kw_only=True)
class Country:
    """A country from the RadioBrowser API."""

    name: str | None = None
    iso_3166_1: str | None = None
    stationcount: int | None = None

    def __post_init__(self):
        if self.name is None:
            self.name = "ΩM4L42rPHqy123PyLavInvalidFallback-un5Nht475B"
