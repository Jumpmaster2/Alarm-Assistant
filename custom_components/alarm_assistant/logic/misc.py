"""Small helpers: cause text, garage network, night door tag and switch off time."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, time, timedelta

WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


def join_names(names: Iterable[str], unknown: str) -> str:
    """Unique names in order, joined with commas."""
    seen: list[str] = []
    for name in names:
        if name and name not in seen:
            seen.append(name)
    return ", ".join(seen) if seen else unknown


def anyone_connected(connections: Iterable[str | None], networks: Iterable[str]) -> bool:
    """At least one phone is connected to one of the networks."""
    names = {str(n).strip() for n in networks if str(n).strip()}
    return any((c or "").strip() in names for c in connections)


def tag_action(is_on: bool, unchanged_for: float | None, min_seconds: float = 10) -> str | None:
    """'on' or 'off' when the tag is scanned (ignored right after a change)."""
    if unchanged_for is not None and unchanged_for < min_seconds:
        return None
    return "off" if is_on else "on"


def next_daily(now: datetime, at: time, weekdays: Iterable[str]) -> datetime | None:
    """Next time ``at`` on one of the weekdays (None: no weekday chosen)."""
    days = {WEEKDAYS.index(d) for d in weekdays if d in WEEKDAYS}
    if not days:
        return None
    for offset in range(8):
        day = (now + timedelta(days=offset)).date()
        candidate = datetime.combine(day, at, tzinfo=now.tzinfo)
        if candidate > now and candidate.weekday() in days:
            return candidate
    return None
