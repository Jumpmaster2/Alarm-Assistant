"""Filters for sensors: motion while the vacuum runs, conditional contacts."""

from __future__ import annotations

INVALID = ("unavailable", "unknown")
VACUUM_ACTIVE = ("cleaning", "returning")


def fault_active(fault_state: str | None) -> bool:
    """The fault sensor reports a problem (or is gone)."""
    return fault_state is not None and (fault_state == "on" or fault_state in INVALID)


def motion_suppressed(
    vacuum_state: str | None,
    vacuum_changed_ago: float | None,
    fault_state: str | None,
    dock_grace: float,
) -> bool:
    """Motion does not count while the vacuum drives, shortly after docking,
    or while the fault sensor is on or not available."""
    if fault_active(fault_state):
        return True
    if vacuum_state in VACUUM_ACTIVE:
        return True
    return (
        vacuum_state == "docked"
        and vacuum_changed_ago is not None
        and vacuum_changed_ago < dock_grace
    )


def contact_counts(condition_state: str | None) -> bool:
    """A conditional contact only counts while its condition entity is not available
    (e.g. a door that stays open for a hose while the air conditioner is set up)."""
    return condition_state is None or condition_state in INVALID


def effective_state(raw: str | None, counts: bool) -> str | None:
    """State used by the alarm: 'off' while the sensor does not count."""
    if raw is None or raw in INVALID:
        return raw
    return raw if counts else "off"
