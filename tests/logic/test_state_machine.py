"""Tests for the panel states, arming check and trips."""

from logic.state_machine import (
    ARMED_AWAY,
    ARMING,
    DISARMED,
    PENDING,
    TRIGGERED,
    TYPE_DOOR,
    TYPE_MOTION,
    TYPE_WINDOW,
    SensorConf,
    SensorTracker,
    check_arm,
    is_trip,
    next_state_on_trip,
    restored_state,
    state_after_trigger,
    type_defaults,
)


def _sensor(entity_id: str, sensor_type: str) -> SensorConf:
    return SensorConf(entity_id, entity_id, sensor_type, **type_defaults(sensor_type))


WINDOW = _sensor("binary_sensor.window", TYPE_WINDOW)
DOOR = _sensor("binary_sensor.door", TYPE_DOOR)
MOTION = _sensor("binary_sensor.motion", TYPE_MOTION)
ALL = [WINDOW, DOOR, MOTION]


def test_open_window_is_bypassed() -> None:
    result = check_arm(ALL, {WINDOW.entity_id}, exit_delay=0)
    assert result.ok
    assert result.bypassed == (WINDOW.entity_id,)


def test_open_door_blocks_without_exit_time() -> None:
    result = check_arm(ALL, {DOOR.entity_id}, exit_delay=0)
    assert not result.ok
    assert result.blocking == (DOOR.entity_id,)


def test_open_door_allowed_during_exit_time() -> None:
    assert check_arm(ALL, {DOOR.entity_id}, exit_delay=30).ok


def test_force_bypasses_door() -> None:
    result = check_arm(ALL, {DOOR.entity_id}, exit_delay=0, force=True)
    assert result.ok
    assert result.bypassed == (DOOR.entity_id,)


def test_active_motion_does_not_block() -> None:
    result = check_arm(ALL, {MOTION.entity_id}, exit_delay=0)
    assert result.ok
    assert result.bypassed == ()


def test_trip_needs_known_off() -> None:
    assert is_trip("off", "on")
    assert not is_trip(None, "on")
    assert not is_trip("on", "on")
    assert not is_trip("off", "unavailable")


def test_tracker_keeps_state_over_unavailable() -> None:
    tracker = SensorTracker()
    assert not tracker.update("a", "off")
    assert not tracker.update("a", "unavailable")
    assert tracker.update("a", "on")
    tracker2 = SensorTracker()
    assert not tracker2.update("b", "unavailable")
    assert not tracker2.update("b", "on")


def test_window_triggers_immediately() -> None:
    assert next_state_on_trip(ARMED_AWAY, WINDOW, 30) == TRIGGERED


def test_door_and_motion_use_entry_delay() -> None:
    assert next_state_on_trip(ARMED_AWAY, DOOR, 30) == PENDING
    assert next_state_on_trip(ARMED_AWAY, MOTION, 30) == PENDING
    assert next_state_on_trip(ARMED_AWAY, DOOR, 0) == TRIGGERED


def test_pending_immediate_sensor_triggers() -> None:
    assert next_state_on_trip(PENDING, WINDOW, 30) == TRIGGERED
    assert next_state_on_trip(PENDING, MOTION, 30) is None


def test_arming_ignores_exit_sensors() -> None:
    assert next_state_on_trip(ARMING, DOOR, 30) is None
    assert next_state_on_trip(ARMING, WINDOW, 30) == TRIGGERED


def test_disarmed_ignores_trips() -> None:
    assert next_state_on_trip(DISARMED, WINDOW, 30) is None
    assert next_state_on_trip(TRIGGERED, WINDOW, 30) is None


def test_after_trigger_and_restore() -> None:
    assert state_after_trigger(False) == ARMED_AWAY
    assert state_after_trigger(True) == DISARMED
    assert restored_state(TRIGGERED) == ARMED_AWAY
    assert restored_state(PENDING) == ARMED_AWAY
    assert restored_state(DISARMED) == DISARMED
    assert restored_state(None) == DISARMED
