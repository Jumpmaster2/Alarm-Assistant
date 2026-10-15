"""Tests for sensor filters, automatic arming, call chain, camera and helpers."""

from datetime import datetime, time, timedelta, timezone

from logic.auto_arm import (
    AutoArmSettings,
    AutoArmState,
    away_by_persons,
    away_by_wifi,
    may_arm,
    may_warn,
    seconds_until_ready,
)
from logic.call import CallSettings, dial_input, normalise_target, plan
from logic.camera import (
    FRIGATE_ALL_OFF,
    FRIGATE_ALL_ON,
    FRIGATE_DETECT_OFF,
    frigate_mode,
    privacy_wanted,
    vacuum_active,
)
from logic.misc import anyone_connected, join_names, next_daily, tag_action
from logic.sensors import contact_counts, effective_state, fault_active, motion_suppressed

# ---------------------------------------------------------------- sensors


def test_motion_suppressed_by_vacuum_and_fault() -> None:
    assert motion_suppressed("cleaning", 10, "off", 120)
    assert motion_suppressed("returning", 10, "off", 120)
    assert motion_suppressed("docked", 60, "off", 120)
    assert not motion_suppressed("docked", 200, "off", 120)
    assert motion_suppressed("docked", 200, "on", 120)
    assert motion_suppressed(None, None, "unavailable", 120)
    assert not motion_suppressed(None, None, None, 120)


def test_fault_active() -> None:
    assert fault_active("on")
    assert fault_active("unknown")
    assert not fault_active("off")
    assert not fault_active(None)


def test_conditional_contact() -> None:
    assert contact_counts("unavailable")
    assert not contact_counts("cool")
    assert contact_counts(None)
    assert effective_state("on", False) == "off"
    assert effective_state("on", True) == "on"
    assert effective_state("unavailable", True) == "unavailable"


# ---------------------------------------------------------------- automatic arming

SETTINGS = AutoArmSettings(quiet=600, prewarn=300, retry_after_disarm=120, presence_stable=120)


def _state(**kwargs) -> AutoArmState:
    values = {
        "enabled": True,
        "disarmed": True,
        "disarmed_for": None,
        "away_for": 600.0,
        "kids_home": False,
        "quiet_for": 700.0,
    }
    values.update(kwargs)
    return AutoArmState(**values)


def test_presence() -> None:
    assert away_by_wifi(["Other", None], ["Home"])
    assert not away_by_wifi(["Home", None], ["Home"])
    assert away_by_persons(["not_home", "work"])
    assert not away_by_persons(["home", "not_home"])


def test_warn_and_arm() -> None:
    assert may_warn(_state(), SETTINGS)
    assert not may_arm(_state(), SETTINGS)
    assert may_arm(_state(quiet_for=900.0), SETTINGS)


def test_blockers() -> None:
    assert not may_warn(_state(kids_home=True), SETTINGS)
    assert not may_warn(_state(enabled=False), SETTINGS)
    assert not may_warn(_state(disarmed=False), SETTINGS)
    assert not may_warn(_state(away_for=None), SETTINGS)
    assert not may_warn(_state(away_for=60.0), SETTINGS)
    assert not may_warn(_state(quiet_for=None), SETTINGS)
    assert not may_warn(_state(quiet_for=300.0), SETTINGS)
    assert not may_warn(_state(disarmed_for=60.0), SETTINGS)
    assert may_warn(_state(disarmed_for=130.0), SETTINGS)


def test_seconds_until_ready() -> None:
    assert seconds_until_ready(_state(quiet_for=500.0), SETTINGS) == 100
    assert seconds_until_ready(_state(away_for=20.0, quiet_for=700.0), SETTINGS) == 100
    assert seconds_until_ready(_state(), SETTINGS) == 0
    assert seconds_until_ready(_state(quiet_for=None), SETTINGS) is None
    assert seconds_until_ready(_state(kids_home=True), SETTINGS) is None


# ---------------------------------------------------------------- call chain

CALL = CallSettings(addon="addon_sip", targets=("sip:first@example.org", "200"), platform="tts.x")


def test_plan_acknowledge_all_but_last() -> None:
    assert plan(CALL) == [("sip:first@example.org", True), ("200", False)]
    assert plan(CallSettings(addon="a", targets=("1",))) == [("1", False)]
    no_ack = CallSettings(addon="a", targets=("1", "2"), acknowledge=False)
    assert plan(no_ack) == [("1", False), ("2", False)]


def test_dial_with_acknowledge() -> None:
    data = dial_input(
        CALL, "sip:first@example.org", "msg", ack_entity="button.ack", ack_message="press 1"
    )
    assert data["addon"] == "addon_sip"
    menu = data["input"]["menu"]
    assert data["input"]["command"] == "dial"
    assert menu["message"] == "press 1"
    assert menu["choices"]["1"]["action"]["entity_id"] == "button.ack"
    assert menu["platform"] == "tts.x"


def test_dial_plain() -> None:
    data = dial_input(CALL, "200", "msg")
    assert data["input"]["number"] == "sip:200"
    assert data["input"]["menu"]["post_action"] == "hangup"
    assert normalise_target(" sip:x ") == "sip:x"


# ---------------------------------------------------------------- camera


def test_vacuum_active() -> None:
    assert vacuum_active("cleaning", True, "on")
    assert vacuum_active("idle", False, "off")
    assert not vacuum_active("docked", True, "on")
    assert not vacuum_active("idle", False, "on")


def test_frigate_mode() -> None:
    assert frigate_mode(True, True, False, False) == FRIGATE_ALL_OFF
    assert frigate_mode(True, False, False, False) == FRIGATE_ALL_ON
    assert frigate_mode(False, False, True, True) == FRIGATE_ALL_OFF
    assert frigate_mode(False, True, False, True) == FRIGATE_DETECT_OFF
    assert frigate_mode(False, True, False, False) == FRIGATE_ALL_ON


def test_privacy_wanted() -> None:
    assert privacy_wanted(True, False, False)
    assert not privacy_wanted(False, False, False)
    assert not privacy_wanted(True, True, False)
    assert not privacy_wanted(True, False, True)


# ---------------------------------------------------------------- helpers


def test_join_names() -> None:
    assert join_names(["A", "B", "A", ""], "unknown") == "A, B"
    assert join_names([], "unknown") == "unknown"


def test_anyone_connected() -> None:
    assert anyone_connected(["Garage", None], ["Garage"])
    assert not anyone_connected(["Home", None], ["Garage"])


def test_tag_action() -> None:
    assert tag_action(False, 20) == "on"
    assert tag_action(True, 20) == "off"
    assert tag_action(True, 5) is None
    assert tag_action(False, None) == "on"


def test_next_daily_weekdays() -> None:
    tz = timezone(timedelta(hours=2))
    friday_noon = datetime(2026, 10, 16, 12, 0, tzinfo=tz)
    nxt = next_daily(friday_noon, time(5, 0), ["mon", "tue", "wed", "thu", "fri"])
    assert nxt == datetime(2026, 10, 19, 5, 0, tzinfo=tz)
    early = datetime(2026, 10, 16, 4, 0, tzinfo=tz)
    assert next_daily(early, time(5, 0), ["fri"]) == datetime(2026, 10, 16, 5, 0, tzinfo=tz)
    assert next_daily(early, time(5, 0), []) is None
