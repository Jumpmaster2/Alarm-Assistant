"""States of the alarm panel and the decisions between them."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

DISARMED = "disarmed"
ARMING = "arming"
ARMED_AWAY = "armed_away"
PENDING = "pending"
TRIGGERED = "triggered"

ARMED_STATES = (ARMING, ARMED_AWAY, PENDING, TRIGGERED)

TYPE_DOOR = "door"
TYPE_WINDOW = "window"
TYPE_MOTION = "motion"
TYPE_OTHER = "other"
SENSOR_TYPES = [TYPE_DOOR, TYPE_WINDOW, TYPE_MOTION, TYPE_OTHER]

ON = "on"
OFF = "off"


@dataclass(frozen=True)
class SensorConf:
    """How one sensor takes part in the alarm."""

    entity_id: str
    name: str
    type: str = TYPE_WINDOW
    entry_delay: bool = False
    exit_delay: bool = False
    auto_bypass: bool = False
    allow_open: bool = False


def type_defaults(sensor_type: str) -> dict[str, bool]:
    """Sensible behaviour per sensor type (the user can change every value)."""
    if sensor_type == TYPE_DOOR:
        return {"entry_delay": True, "exit_delay": True, "auto_bypass": False, "allow_open": False}
    if sensor_type == TYPE_MOTION:
        return {"entry_delay": True, "exit_delay": True, "auto_bypass": False, "allow_open": True}
    if sensor_type == TYPE_WINDOW:
        return {"entry_delay": False, "exit_delay": False, "auto_bypass": True, "allow_open": False}
    return {"entry_delay": False, "exit_delay": False, "auto_bypass": False, "allow_open": False}


@dataclass(frozen=True)
class ArmCheck:
    """Result of the check before arming."""

    blocking: tuple[str, ...] = ()
    bypassed: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.blocking


def check_arm(
    sensors: Iterable[SensorConf], open_ids: set[str], exit_delay: float, force: bool = False
) -> ArmCheck:
    """Which open sensors block arming and which are ignored until disarming.

    - motion style sensors (``allow_open``) may be active, they only count again
      after they changed
    - sensors with exit delay may be open while there is an exit time
    - ``auto_bypass`` sensors (open windows) are ignored until disarming
    - ``force`` ignores every other open sensor as well
    """
    blocking: list[str] = []
    bypassed: list[str] = []
    for sensor in sensors:
        if sensor.entity_id not in open_ids or sensor.allow_open:
            continue
        if sensor.exit_delay and exit_delay > 0:
            continue
        if sensor.auto_bypass or force:
            bypassed.append(sensor.entity_id)
        else:
            blocking.append(sensor.entity_id)
    return ArmCheck(tuple(blocking), tuple(bypassed))


def is_trip(previous: str | None, new: str | None) -> bool:
    """A sensor trips when it changes from a known 'off' to 'on'.

    ``previous`` is the last valid state, so a sensor that was closed, became
    unavailable and comes back open still trips. A sensor without a known
    previous state (start of Home Assistant) never trips.
    """
    return new == ON and previous == OFF


def next_state_on_trip(state: str, sensor: SensorConf, entry_delay: float) -> str | None:
    """New panel state when ``sensor`` trips (None: nothing happens)."""
    delayed = sensor.entry_delay and entry_delay > 0
    if state == ARMED_AWAY:
        return PENDING if delayed else TRIGGERED
    if state == ARMING:
        if sensor.exit_delay:
            return None
        return PENDING if delayed else TRIGGERED
    if state == PENDING:
        return None if sensor.entry_delay else TRIGGERED
    return None


def state_after_trigger(disarm_after_trigger: bool) -> str:
    """State when the trigger time is over."""
    return DISARMED if disarm_after_trigger else ARMED_AWAY


def restored_state(stored: str | None) -> str:
    """State after a restart: armed stays armed, a running alarm is not repeated."""
    if stored in ARMED_STATES:
        return ARMED_AWAY
    return DISARMED


@dataclass
class SensorTracker:
    """Last valid state per sensor, used to detect trips across unavailable phases."""

    last_valid: dict[str, str] = field(default_factory=dict)

    def update(self, entity_id: str, new: str | None) -> bool:
        """Remember ``new`` and return True when it is a trip."""
        previous = self.last_valid.get(entity_id)
        if new in (ON, OFF):
            self.last_valid[entity_id] = new
        return is_trip(previous, new)
