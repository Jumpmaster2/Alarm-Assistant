"""Rules for the camera: privacy mode, preset and detection switches."""

from __future__ import annotations

FRIGATE_ALL_ON = "all_on"
FRIGATE_ALL_OFF = "all_off"
FRIGATE_DETECT_OFF = "detect_off"


def vacuum_active(state: str | None, is_docked: object, charging: str | None) -> bool:
    """Vacuum drives (or stands somewhere without charging)."""
    if state in ("cleaning", "returning"):
        return True
    return is_docked is False and charging == "off"


def frigate_mode(live: bool, disarmed: bool, kids_home: bool, vacuum: bool) -> str:
    """Which detection switches are on.

    Live view (only while disarmed) and children at home turn everything off;
    a driving vacuum keeps recordings but turns detection off.
    """
    if live and disarmed:
        return FRIGATE_ALL_OFF
    if kids_home:
        return FRIGATE_ALL_OFF
    if vacuum:
        return FRIGATE_DETECT_OFF
    return FRIGATE_ALL_ON


def privacy_wanted(disarmed: bool, kids_home: bool, live: bool) -> bool:
    """Privacy mode on: disarmed, no children alone, no live view."""
    return disarmed and not kids_home and not live
