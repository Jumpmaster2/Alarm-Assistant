"""Automatic arming when everybody is away."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

MODE_WIFI = "wifi"
MODE_PERSONS = "persons"
PRESENCE_MODES = [MODE_WIFI, MODE_PERSONS]
UNKNOWN_HOME = "home"
UNKNOWN_AWAY = "away"
UNKNOWN_PRESENCE = [UNKNOWN_HOME, UNKNOWN_AWAY]
UNKNOWN_STATES = (None, "", "unavailable", "unknown")


def _unknown(state: str | None) -> bool:
    return state is None or state.strip() in UNKNOWN_STATES


def at_home_by_wifi(
    connection: str | None, home_networks: Iterable[str], unknown_home: bool = False
) -> bool:
    """The phone is connected to a home network (or unknown and counted as at home)."""
    if _unknown(connection):
        return unknown_home
    homes = {str(n).strip() for n in home_networks if str(n).strip()}
    return str(connection).strip() in homes


def away_by_wifi(
    connections: Iterable[str | None], home_networks: Iterable[str], unknown_home: bool = False
) -> bool:
    """Nobody is connected to a home network.

    A phone without a known state (switched off, empty battery, app not
    reporting) counts as at home with ``unknown_home``, else as away.
    """
    homes = list(home_networks)
    return not any(at_home_by_wifi(c, homes, unknown_home) for c in connections)


def away_by_persons(states: Iterable[str | None], unknown_home: bool = False) -> bool:
    """No person is at home."""
    return not any(s == "home" or (unknown_home and _unknown(s)) for s in states)


@dataclass(frozen=True)
class AutoArmState:
    """Facts at one moment (durations in seconds, None: condition not met)."""

    enabled: bool
    disarmed: bool
    disarmed_for: float | None
    away_for: float | None
    kids_home: bool
    quiet_for: float | None


@dataclass(frozen=True)
class AutoArmSettings:
    quiet: float = 600
    prewarn: float = 300
    retry_after_disarm: float = 120
    presence_stable: float = 120


def basic_ok(state: AutoArmState, settings: AutoArmSettings) -> bool:
    """Everything except the motion time."""
    return (
        state.enabled
        and state.disarmed
        and not state.kids_home
        and state.away_for is not None
        and state.away_for >= settings.presence_stable
        and (state.disarmed_for is None or state.disarmed_for >= settings.retry_after_disarm)
    )


def may_warn(state: AutoArmState, settings: AutoArmSettings) -> bool:
    """Start the warning: away and no motion for the quiet time."""
    return (
        basic_ok(state, settings)
        and state.quiet_for is not None
        and state.quiet_for >= settings.quiet
    )


def may_arm(state: AutoArmState, settings: AutoArmSettings) -> bool:
    """Arm after the warning: still away and no motion since before the warning."""
    return (
        basic_ok(state, settings)
        and state.quiet_for is not None
        and state.quiet_for >= settings.quiet + settings.prewarn
    )


def seconds_until_ready(state: AutoArmState, settings: AutoArmSettings) -> float | None:
    """When the warning could start if nothing changes (None: not foreseeable)."""
    if (
        not state.enabled
        or not state.disarmed
        or state.kids_home
        or state.away_for is None
        or state.quiet_for is None
    ):
        return None
    waits = [settings.presence_stable - state.away_for, settings.quiet - state.quiet_for]
    if state.disarmed_for is not None:
        waits.append(settings.retry_after_disarm - state.disarmed_for)
    return max(0.0, *waits)
