"""Scenarios of the engine with a Home Assistant test instance."""

from __future__ import annotations

import pytest
from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentryData
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import issue_registry as ir

from custom_components.alarm_assistant.const import (
    DOMAIN,
    SUBENTRY_CAMERA,
    SUBENTRY_GARAGE,
    SUBENTRY_PERSON,
)
from custom_components.alarm_assistant.logic.code import hash_code, legacy_hash, verify_code

from .conftest import (
    AIRCON,
    BALCONY,
    BALCONY_COVER,
    DOOR,
    FAULT,
    HOME,
    LOCK,
    MOTION,
    PANEL,
    VACUUM,
    WIFI_A,
    WIFI_B,
    WINDOW,
    advance,
    calls_of,
    make_entry,
    set_state,
    setup_entry,
)

START = "2026-10-15 12:00:00+02:00"
KIDS = "switch.alarm_assistant_children_alone_at_home"
AUTO = "switch.alarm_assistant_automatic_arming"
NIGHT = "switch.alarm_assistant_night_door_alarm"
LIVE = "switch.alarm_assistant_camera_live_view"
ACK = "button.alarm_assistant_acknowledge_call"
CAUSE = "sensor.alarm_assistant_cause"

REACTIONS = {
    "announce_entities": ["notify.everywhere"],
    "volume_players": ["media_player.kitchen"],
    "sound_devices": ["device1"],
    "speak_services": ["notify.speaker"],
    "turn_on_entities": ["light.hall", "switch.baby_monitor"],
    "close_covers": ["cover.living"],
    "lock": LOCK,
    "lock_door_sensor": DOOR,
}


async def _arm(hass: HomeAssistant, code: str | None = None) -> None:
    data = {"entity_id": PANEL}
    if code is not None:
        data["code"] = code
    await hass.services.async_call("alarm_control_panel", "alarm_arm_away", data, blocking=True)
    await hass.async_block_till_done(wait_background_tasks=True)


async def _disarm(hass: HomeAssistant, code: str | None = None) -> None:
    data = {"entity_id": PANEL}
    if code is not None:
        data["code"] = code
    await hass.services.async_call("alarm_control_panel", "alarm_disarm", data, blocking=True)
    await hass.async_block_till_done(wait_background_tasks=True)


def _state(hass: HomeAssistant) -> str:
    return hass.states.get(PANEL).state


async def test_arm_with_open_window_bypasses_and_locks(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(**REACTIONS))
    await set_state(hass, WINDOW, "on")
    await _arm(hass)
    assert _state(hass) == "armed_away"
    assert hass.states.get(PANEL).attributes["bypassed_sensors"] == [WINDOW]
    assert any("Kitchen window" in c.data["message"] for c in calls["notify"])
    assert [c.data["entity_id"] for c in calls["lock"]] == [LOCK]
    # the bypassed window does not trigger
    await set_state(hass, WINDOW, "off")
    await set_state(hass, WINDOW, "on")
    assert _state(hass) == "armed_away"


async def test_open_door_blocks_arming(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await set_state(hass, DOOR, "on")
    with pytest.raises(ServiceValidationError):
        await _arm(hass)
    assert _state(hass) == "disarmed"
    assert any("Front door" in c.data["message"] for c in calls["notify"])


async def test_motion_entry_delay_then_alarm(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(**REACTIONS))
    await _arm(hass)
    await set_state(hass, MOTION, "on")
    assert _state(hass) == "pending"
    assert calls["send_message"][0].data["entity_id"] == "notify.everywhere"
    await advance(hass, freezer, 25)
    assert _state(hass) == "pending"
    await advance(hass, freezer, 10)
    assert _state(hass) == "triggered"
    assert hass.states.get(CAUSE).state == "Hall motion"
    assert any("Hall motion" in c.data["message"] for c in calls["notify"])
    assert len(calls["pushover"]) == 1
    assert {c.data["entity_id"] for c in calls["turn_on"]} == {"light.hall", "switch.baby_monitor"}
    assert calls["close_cover"][0].data["entity_id"] == "cover.living"
    assert [c.data["volume_level"] for c in calls["volume"]] == [0.51, 0.2]
    assert calls["sound"][0].data["device_id"] == "device1"
    assert len(calls["speak"]) == 1
    # back to armed after the trigger time
    await advance(hass, freezer, 1800)
    assert _state(hass) == "armed_away"


async def test_window_triggers_immediately_and_disarm(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await _arm(hass)
    await set_state(hass, WINDOW, "on")
    assert _state(hass) == "triggered"
    await _disarm(hass)
    assert _state(hass) == "disarmed"


async def test_disarm_during_entry_delay(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await _arm(hass)
    await set_state(hass, DOOR, "on")
    assert _state(hass) == "pending"
    await _disarm(hass)
    await advance(hass, freezer, 60)
    assert _state(hass) == "disarmed"
    assert calls["pushover"] == []


async def test_unavailable_sensor_does_not_trigger_but_reopen_does(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await _arm(hass)
    await set_state(hass, WINDOW, "unavailable")
    assert _state(hass) == "armed_away"
    await set_state(hass, WINDOW, "on")
    assert _state(hass) == "triggered"


async def test_vacuum_suppresses_motion(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await _arm(hass)
    await set_state(hass, VACUUM, "cleaning", {"is_docked": False})
    await set_state(hass, MOTION, "on")
    assert _state(hass) == "armed_away"
    assert hass.states.get("binary_sensor.alarm_assistant_motion_suppressed").state == "on"
    await set_state(hass, VACUUM, "docked", {"is_docked": True})
    await advance(hass, freezer, 60)
    assert _state(hass) == "armed_away"
    # grace time over and the sensor still reports motion: it counts now
    await advance(hass, freezer, 70)
    assert _state(hass) == "pending"


async def test_fault_sensor_messages(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await set_state(hass, FAULT, "on")
    assert len(calls["admin"]) == 1
    await _arm(hass)
    await set_state(hass, MOTION, "on")
    assert _state(hass) == "armed_away"
    assert len(calls["admin"]) == 2


async def test_conditional_balcony_door(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await set_state(hass, AIRCON, "cool")
    await set_state(hass, BALCONY, "on")
    await _arm(hass)
    assert _state(hass) == "armed_away"
    assert hass.states.get(PANEL).attributes["bypassed_sensors"] == []
    assert calls["set_cover_position"][0].data == {"entity_id": BALCONY_COVER, "position": 20}
    # air conditioner removed while the door is open: the door counts and triggers
    await set_state(hass, AIRCON, "unavailable")
    assert _state(hass) == "triggered"


async def test_unlocking_disarms(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(lock=LOCK))
    await set_state(hass, LOCK, "locked")
    await _arm(hass)
    await set_state(hass, LOCK, "unlocked")
    assert _state(hass) == "disarmed"


async def test_lock_falling_back_does_not_disarm(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(**REACTIONS))
    await _arm(hass)
    assert len(calls["lock"]) == 1
    # the lock reports locked and falls back to unlocked seconds later
    await set_state(hass, LOCK, "locking")
    await set_state(hass, LOCK, "locked")
    await advance(hass, freezer, 3)
    await set_state(hass, LOCK, "unlocked")
    assert _state(hass) == "armed_away"
    assert any("retried" in c.data["message"] for c in calls["notify"])
    # one retry, a second failure only warns
    await advance(hass, freezer, 11)
    assert len(calls["lock"]) == 2
    await set_state(hass, LOCK, "locked")
    await set_state(hass, LOCK, "unlocked")
    assert _state(hass) == "armed_away"
    assert any("again" in c.data["message"] for c in calls["notify"])
    await advance(hass, freezer, 30)
    assert len(calls["lock"]) == 2
    # unlocking later is a person: disarms
    await set_state(hass, LOCK, "locked")
    await set_state(hass, LOCK, "opening")
    assert _state(hass) == "disarmed"


async def test_code(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(code=hash_code("1234")))
    await _arm(hass)
    with pytest.raises(ServiceValidationError):
        await _disarm(hass, "0000")
    assert _state(hass) == "armed_away"
    await _disarm(hass, "1234")
    assert _state(hass) == "disarmed"


async def test_legacy_code_is_upgraded_without_reload(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    """A code hash of version 0.4 still works and is stored salted afterwards."""
    freezer.move_to(START)
    entry = make_entry(code=legacy_hash("1234"))
    await setup_entry(hass, entry)
    engine = entry.runtime_data
    await _arm(hass)
    await _disarm(hass, "1234")
    await hass.async_block_till_done()
    assert _state(hass) == "disarmed"
    assert entry.options["code"].startswith("pbkdf2_sha256$")
    assert verify_code("1234", entry.options["code"])
    assert entry.runtime_data is engine  # no reload for the new hash


async def test_wrong_codes_are_reported(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(code=hash_code("1234")))
    await _arm(hass)
    for _ in range(5):
        with pytest.raises(ServiceValidationError):
            await _disarm(hass, "0000")
    await hass.async_block_till_done()
    assert any("5 times" in c.data["message"] for c in calls["notify"])
    assert _state(hass) == "armed_away"


AUTO_ARM = {
    "wifi_sensors": [WIFI_A, WIFI_B],
    "home_networks": [HOME],
}


async def test_automatic_arming(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(**AUTO_ARM))
    await set_state(hass, WIFI_A, "Mobile")
    await set_state(hass, WIFI_B, "<not connected>")
    # last motion 30 min ago: the presence must be stable for 2 min
    await advance(hass, freezer, 60)
    assert not any("Nobody" in c.data["message"] for c in calls["notify"])
    await advance(hass, freezer, 90)
    assert any("Nobody" in c.data["message"] for c in calls["notify"])
    assert hass.states.get("binary_sensor.alarm_assistant_automatic_arming_warning").state == "on"
    await advance(hass, freezer, 5 * 60 + 30)
    assert _state(hass) == "armed_away"


@pytest.mark.parametrize(("unknown", "armed"), [("home", False), ("away", True)])
async def test_unknown_phone_counts_as_option(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory, unknown, armed
) -> None:
    """A phone that is unavailable counts as at home by default."""
    freezer.move_to(START)
    await setup_entry(hass, make_entry(**AUTO_ARM, unknown_presence=unknown))
    await set_state(hass, WIFI_A, "Mobile")
    await set_state(hass, WIFI_B, "unavailable")
    await advance(hass, freezer, 10 * 60)
    assert (_state(hass) == "armed_away") is armed


async def test_automatic_arming_blocked_by_kids_and_motion(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(**AUTO_ARM))
    await hass.services.async_call("switch", "turn_on", {"entity_id": KIDS}, blocking=True)
    await set_state(hass, WIFI_A, "Mobile")
    await set_state(hass, WIFI_B, "Mobile")
    await advance(hass, freezer, 20 * 60)
    assert _state(hass) == "disarmed"
    await hass.services.async_call("switch", "turn_off", {"entity_id": KIDS}, blocking=True)
    await hass.async_block_till_done(wait_background_tasks=True)
    # warning starts; motion during the warning prevents arming
    await advance(hass, freezer, 60)
    assert hass.states.get("binary_sensor.alarm_assistant_automatic_arming_warning").state == "on"
    await set_state(hass, MOTION, "on")
    await set_state(hass, MOTION, "off")
    await advance(hass, freezer, 6 * 60)
    assert _state(hass) == "disarmed"


async def test_call_chain_with_acknowledge(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory, no_pauses
) -> None:
    freezer.move_to(START)
    acked = {"done": False}

    async def press_during_wait(seconds: float) -> None:
        if seconds == 50 and acked["done"]:
            await hass.services.async_call("button", "press", {"entity_id": ACK}, blocking=True)

    no_pauses.side_effect = press_during_wait
    options = {"call_addon": "sip_addon", "call_targets": ["sip:first@x", "sip:second@x"]}
    await setup_entry(hass, make_entry(**options))
    await _arm(hass)
    await set_state(hass, WINDOW, "on")
    await hass.async_block_till_done(wait_background_tasks=True)
    numbers = [c.data["input"]["number"] for c in calls["stdin"]]
    assert numbers == ["sip:first@x", "sip:second@x"]
    first = calls["stdin"][0].data["input"]["menu"]
    assert first["choices"]["1"]["action"]["entity_id"] == ACK
    assert "Calling now" in calls["notify"][-1].data["message"]
    # second alarm within the cooldown: no new call, but the push
    pushes = len(calls["pushover"])
    await _disarm(hass)
    await set_state(hass, WINDOW, "off")
    await _arm(hass)
    await set_state(hass, WINDOW, "on")
    assert len(calls["stdin"]) == 2
    assert len(calls["pushover"]) == pushes + 1
    assert "Calling now" not in calls["notify"][-1].data["message"]
    # after the cooldown, acknowledged call stops the chain
    await _disarm(hass)
    await advance(hass, freezer, 200)
    acked["done"] = True
    await set_state(hass, WINDOW, "off")
    await _arm(hass)
    await set_state(hass, WINDOW, "on")
    await hass.async_block_till_done(wait_background_tasks=True)
    assert len(calls["stdin"]) == 3


async def test_disarm_stops_call_chain_and_siren(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory, no_pauses
) -> None:
    """Disarming during the alarm: no further calls, the volume goes back."""
    freezer.move_to(START)
    entry = make_entry(
        **REACTIONS, call_addon="sip_addon", call_targets=["sip:1@x", "sip:2@x", "sip:3@x"]
    )
    await setup_entry(hass, entry)

    async def disarm_while_waiting(seconds: float) -> None:
        if seconds == 50:
            entry.runtime_data.disarm()

    no_pauses.side_effect = disarm_while_waiting
    await _arm(hass)
    await set_state(hass, WINDOW, "on")
    await hass.async_block_till_done(wait_background_tasks=True)
    assert _state(hass) == "disarmed"
    assert [c.data["input"]["number"] for c in calls["stdin"]] == ["sip:1@x"]
    assert calls["volume"][-1].data["volume_level"] == 0.2


async def test_state_survives_reload(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    entry = make_entry()
    await setup_entry(hass, entry)
    await _arm(hass)
    await set_state(hass, WINDOW, "on")
    assert _state(hass) == "triggered"
    await hass.services.async_call("switch", "turn_on", {"entity_id": KIDS}, blocking=True)
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done(wait_background_tasks=True)
    assert _state(hass) == "armed_away"
    assert hass.states.get(KIDS).state == "on"


async def test_night_door_alarm(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to("2026-10-15 22:00:00+02:00")  # Thursday
    options = {
        "night_door_sensor": DOOR,
        "night_tag": "tag-1",
        "night_turn_on_entities": ["light.dining"],
        "night_volume_players": ["media_player.kitchen"],
        "night_sound_devices": ["device1"],
        "night_speak_services": ["notify.speaker"],
        "night_off_speak_services": ["notify.speaker"],
    }
    await setup_entry(hass, make_entry(**options))
    hass.bus.async_fire("tag_scanned", {"tag_id": "tag-1"})
    await hass.async_block_till_done(wait_background_tasks=True)
    assert hass.states.get(NIGHT).state == "on"
    assert any("Door alarm is on" in c.data["message"] for c in calls["notify"])
    # a second scan right after is ignored
    hass.bus.async_fire("tag_scanned", {"tag_id": "tag-1"})
    await hass.async_block_till_done(wait_background_tasks=True)
    assert hass.states.get(NIGHT).state == "on"
    await set_state(hass, DOOR, "on")
    assert calls["light_on"][0].data == {"entity_id": "light.dining", "brightness_pct": 100}
    assert calls["sound"][0].data["device_id"] == "device1"
    assert calls["speak"][0].data["message"] == "Alarm, door opened"
    assert _state(hass) == "disarmed"
    # switched off automatically at 05:00 on a weekday
    await advance(hass, freezer, 7 * 3600 + 60, step=600)
    assert hass.states.get(NIGHT).state == "off"


async def test_window_hint(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    options = {"hint_door_sensor": DOOR, "hint_windows": [WINDOW], "hint_entity": "switch.lamp"}
    await setup_entry(hass, make_entry(**options))
    await set_state(hass, DOOR, "on")
    assert calls["turn_on"] == []
    await set_state(hass, DOOR, "off")
    await set_state(hass, WINDOW, "on")
    await set_state(hass, DOOR, "on")
    assert calls["turn_on"][0].data["entity_id"] == "switch.lamp"
    assert calls["turn_off"][0].data["entity_id"] == "switch.lamp"


CAMERA = ConfigSubentryData(
    data={
        "privacy_switch": "switch.cam_privacy",
        "ptz_select": "select.cam_ptz",
        "ptz_home_preset": "Living",
        "privacy_delay": 2,
        "record_switches": ["switch.cam_record"],
        "detect_switches": ["switch.cam_detect"],
        "person_sensor": "binary_sensor.cam_person",
        "person_image": "image.cam_person",
        "person_push": True,
    },
    subentry_id="cam1",
    subentry_type=SUBENTRY_CAMERA,
    title="Living cam",
    unique_id=None,
)


async def test_camera_rules(
    hass: HomeAssistant, base_states, calls, service_events, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    hass.states.async_set("switch.cam_privacy", "on")
    hass.states.async_set("switch.cam_record", "on")
    hass.states.async_set("switch.cam_detect", "on")
    hass.states.async_set("binary_sensor.cam_person", "off")
    hass.states.async_set("image.cam_person", "x", {"entity_picture": "/api/image/1"})
    await setup_entry(hass, make_entry(extra_subentries=[CAMERA]))
    await _arm(hass)
    assert calls_of(service_events, "switch", "turn_off")[-1]["entity_id"] == "switch.cam_privacy"
    assert calls["select"][-1].data["option"] == "Living"
    # motion while armed: preset of the motion sensor
    await set_state(hass, VACUUM, "cleaning", {"is_docked": False})
    await set_state(hass, MOTION, "on")
    assert calls["select"][-1].data["option"] == "Hall"
    # detection off while the vacuum drives
    offs = [c["entity_id"] for c in calls_of(service_events, "switch", "turn_off")]
    assert ["switch.cam_detect"] in offs
    # person while armed: push
    await set_state(hass, "binary_sensor.cam_person", "on")
    assert any(c.data["title"] == "Person detected" for c in calls["notify"])
    # disarmed: privacy on after 2 minutes
    await set_state(hass, VACUUM, "docked", {"is_docked": True})
    await _disarm(hass)
    on = calls_of(service_events, "switch", "turn_on")
    privacy_on = [c for c in on if c["entity_id"] == "switch.cam_privacy"]
    assert privacy_on  # the pause is patched, the delay is a pause too
    # children alone at home: privacy off, recording and detection off
    service_events.clear()
    await hass.services.async_call("switch", "turn_on", {"entity_id": KIDS}, blocking=True)
    await hass.async_block_till_done(wait_background_tasks=True)
    off = [c["entity_id"] for c in calls_of(service_events, "switch", "turn_off")]
    assert "switch.cam_privacy" in off
    assert ["switch.cam_record", "switch.cam_detect"] in off


def _switched(service_events, service: str) -> list[str]:
    return [e for c in calls_of(service_events, "switch", service) for e in c["entity_id"]]


async def test_frigate_switches_set_again(
    hass: HomeAssistant, base_states, calls, service_events, freezer: FrozenDateTimeFactory
) -> None:
    """Frigate restarts or someone switches: the rules are applied again."""
    freezer.move_to(START)
    hass.states.async_set("switch.cam_privacy", "on")
    hass.states.async_set("switch.cam_record", "on")
    # detection is not loaded yet when Home Assistant starts
    await setup_entry(hass, make_entry(extra_subentries=[CAMERA]))
    await _arm(hass)
    service_events.clear()
    # detection appears (off after a Frigate restart): switched on after the pause
    await set_state(hass, "switch.cam_detect", "off")
    await advance(hass, freezer, 5, step=5)
    assert _switched(service_events, "turn_on") == []
    await advance(hass, freezer, 6, step=6)
    assert "switch.cam_detect" in _switched(service_events, "turn_on")
    await set_state(hass, "switch.cam_detect", "on")
    # Frigate restarts: unavailable, back with its start value
    service_events.clear()
    await set_state(hass, "switch.cam_record", "unavailable")
    await set_state(hass, "switch.cam_detect", "unavailable")
    await advance(hass, freezer, 20, step=10)
    assert _switched(service_events, "turn_on") == []
    await set_state(hass, "switch.cam_record", "on")
    await set_state(hass, "switch.cam_detect", "off")
    await advance(hass, freezer, 11, step=11)
    assert "switch.cam_detect" in _switched(service_events, "turn_on")
    await set_state(hass, "switch.cam_detect", "on")
    # back in the wanted state: nothing to do
    service_events.clear()
    await set_state(hass, "switch.cam_detect", "unavailable")
    await set_state(hass, "switch.cam_detect", "on")
    await advance(hass, freezer, 20, step=10)
    assert _switched(service_events, "turn_on") == []
    # a switch that does not follow is set again only a few times
    await advance(hass, freezer, 600, step=60)
    for _ in range(5):
        await set_state(hass, "switch.cam_detect", "off")
        await advance(hass, freezer, 11, step=11)
        await set_state(hass, "switch.cam_detect", "on")
    assert _switched(service_events, "turn_on").count("switch.cam_detect") == 3
    # an own change of the rules is no deviation: detection off for the vacuum
    service_events.clear()
    await set_state(hass, VACUUM, "cleaning", {"is_docked": False})
    assert "switch.cam_detect" in _switched(service_events, "turn_off")
    await set_state(hass, "switch.cam_detect", "off")
    await advance(hass, freezer, 20, step=10)
    assert "switch.cam_detect" not in _switched(service_events, "turn_on")


GARAGE = ConfigSubentryData(
    data={
        "garage_panel": "alarm_control_panel.garage",
        "garage_networks": ["GarageNet"],
        "garage_arm_delay": 2,
        "garage_motion": ["binary_sensor.garage_motion"],
        "garage_tts_services": ["notify.phone"],
        "garage_tts_repeat": 2,
    },
    subentry_id="garage1",
    subentry_type=SUBENTRY_GARAGE,
    title="Garage",
    unique_id=None,
)


async def test_garage(
    hass: HomeAssistant, base_states, calls, service_events, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    hass.states.async_set("alarm_control_panel.garage", "armed_away")
    hass.states.async_set("binary_sensor.garage_motion", "off")
    await setup_entry(hass, make_entry(extra_subentries=[GARAGE], wifi_sensors=[WIFI_A, WIFI_B]))
    await set_state(hass, "binary_sensor.garage_motion", "on")
    assert any(c.data["title"] == "Garage" for c in calls["notify"])
    tts = [c.data["data"] for c in calls["notify"] if c.data["message"] == "TTS"]
    assert len(tts) == 2
    assert tts[0]["media_stream"] == "alarm_stream_max"
    assert tts[0]["tts_language"] == "en-US"
    await set_state(hass, WIFI_A, "GarageNet")
    assert (
        calls_of(service_events, "alarm_control_panel", "alarm_disarm")[0]["entity_id"]
        == "alarm_control_panel.garage"
    )
    hass.states.async_set("alarm_control_panel.garage", "disarmed")
    await set_state(hass, WIFI_A, "Mobile")
    await advance(hass, freezer, 60)
    assert calls_of(service_events, "alarm_control_panel", "alarm_arm_away") == []
    await advance(hass, freezer, 70)
    assert (
        calls_of(service_events, "alarm_control_panel", "alarm_arm_away")[0]["entity_id"]
        == "alarm_control_panel.garage"
    )


async def test_missing_entities_issue(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(turn_on_entities=["light.does_not_exist"]))
    issue = ir.async_get(hass).async_get_issue(DOMAIN, "missing_entities")
    assert issue is not None
    assert "light.does_not_exist" in issue.translation_placeholders["entities"]


async def test_call_without_supervisor_is_reported(
    hass: HomeAssistant, base_states, freezer: FrozenDateTimeFactory
) -> None:
    """Without the Supervisor there is no hassio.addon_stdin: shown under repairs."""
    freezer.move_to(START)
    await setup_entry(hass, make_entry(call_addon="abcd_ha-sip", call_targets=["sip:1@x"]))
    issue = ir.async_get(hass).async_get_issue(DOMAIN, "missing_entities")
    assert issue is not None
    assert "hassio.addon_stdin" in issue.translation_placeholders["entities"]


async def test_test_button(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    await set_state(hass, WINDOW, "on")
    await hass.services.async_call(
        "button", "press", {"entity_id": "button.alarm_assistant_test_message"}, blocking=True
    )
    await hass.async_block_till_done(wait_background_tasks=True)
    assert "Kitchen window" in calls["notify"][-1].data["message"]
    assert _state(hass) == "disarmed"


def _person(sub_id: str, name: str, sensor: str) -> ConfigSubentryData:
    return ConfigSubentryData(
        data={"wifi_sensor": sensor},
        subentry_id=sub_id,
        subentry_type=SUBENTRY_PERSON,
        title=name,
        unique_id=None,
    )


async def test_persons_by_wifi(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    persons = [_person("p_a", "Alex", WIFI_A), _person("p_b", "Bo", WIFI_B)]
    await setup_entry(hass, make_entry(extra_subentries=persons, home_networks=[HOME]))
    alex = "binary_sensor.alarm_assistant_alex_at_home"
    assert hass.states.get(alex).state == "on"
    await set_state(hass, WIFI_A, "Mobile")
    assert hass.states.get(alex).state == "off"
    assert hass.states.get("binary_sensor.alarm_assistant_bo_at_home").state == "on"
    await advance(hass, freezer, 20 * 60)
    assert _state(hass) == "disarmed"
    # the last person leaves: warning, then armed
    await set_state(hass, WIFI_B, "<not connected>")
    await advance(hass, freezer, 150)
    assert any("Nobody" in c.data["message"] for c in calls["notify"])
    await advance(hass, freezer, 5 * 60 + 30)
    assert _state(hass) == "armed_away"


async def test_night_door_tag_off_announcement(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    options = {
        "night_door_sensor": DOOR,
        "night_tag": "tag-1",
        "night_volume_players": ["media_player.kitchen", "media_player.bedroom"],
        "night_off_speak_services": ["notify.speaker"],
        "night_off_volume_players": ["media_player.kitchen"],
    }
    await setup_entry(hass, make_entry(**options))
    hass.bus.async_fire("tag_scanned", {"tag_id": "tag-1"})
    await hass.async_block_till_done(wait_background_tasks=True)
    await advance(hass, freezer, 15)
    hass.bus.async_fire("tag_scanned", {"tag_id": "tag-1"})
    await hass.async_block_till_done(wait_background_tasks=True)
    assert hass.states.get(NIGHT).state == "off"
    assert calls["volume"][-1].data == {
        "entity_id": ["media_player.kitchen"],
        "volume_level": 0.3,
    }
    assert calls["speak"][-1].data["message"] == "Alarm is disarmed"


async def test_test_alarm_with_reactions_switched_off(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    options = {**REACTIONS, "call_addon": "sip_addon", "call_targets": ["sip:a@x", "sip:b@x"]}
    entry = make_entry(**options)
    await setup_entry(hass, entry)
    engine = entry.runtime_data
    disabled = ["push:notify.pushover", "lights", "covers", "lock", "call:sip:b@x", "sound"]
    assert engine.arm_test(disabled).ok
    await hass.async_block_till_done(wait_background_tasks=True)
    panel = hass.states.get(PANEL)
    assert panel.state == "armed_away"
    assert panel.attributes["test_mode"] is True
    assert calls["lock"] == []
    assert engine.simulate_trigger()
    await hass.async_block_till_done(wait_background_tasks=True)
    assert _state(hass) == "triggered"
    assert calls["pushover"] == []
    assert calls["turn_on"] == []
    assert calls["close_cover"] == []
    assert calls["sound"] == []
    assert [c.data["input"]["number"] for c in calls["stdin"]] == ["sip:a@x"]
    assert calls["notify"][-1].data["title"].startswith("[TEST]")
    assert calls["send_message"][-1].data["message"].startswith("Attention, this is only a test.")
    assert calls["speak"][-1].data["message"].startswith("Attention, this is only a test.")
    assert hass.states.get(CAUSE).state == "Test trigger"
    # the test survives a reload and ends with disarming
    assert await hass.config_entries.async_reload(entry.entry_id)
    await hass.async_block_till_done()
    assert hass.states.get(PANEL).attributes["test_mode"] is True
    await _disarm(hass)
    assert hass.states.get(PANEL).attributes["test_mode"] is False
    assert entry.runtime_data.test_last == sorted(disabled)


async def test_simulate_only_in_test_mode(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    await _arm(hass)
    assert not entry.runtime_data.simulate_trigger()
    assert _state(hass) == "armed_away"


async def test_lock_coming_back_does_not_disarm(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    """A lock that reconnects reports 'unlocked' again: no unlocking by a person."""
    freezer.move_to(START)
    await setup_entry(hass, make_entry(lock=LOCK))
    await set_state(hass, LOCK, "unavailable")
    await _arm(hass)
    await set_state(hass, LOCK, "unlocked")
    assert _state(hass) == "armed_away"
    await set_state(hass, LOCK, "locked")
    await set_state(hass, LOCK, "unlocked")
    assert _state(hass) == "disarmed"


async def test_jammed_lock_warns_and_retries(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(**REACTIONS))
    await _arm(hass)
    assert len(calls["lock"]) == 1
    await set_state(hass, LOCK, "locking")
    await set_state(hass, LOCK, "jammed")
    assert _state(hass) == "armed_away"
    assert any("retried" in c.data["message"] for c in calls["notify"])
    await advance(hass, freezer, 11)
    assert len(calls["lock"]) == 2


async def test_unavailable_sensor_is_reported_while_armed(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry())
    # disarmed: nothing is reported
    await set_state(hass, DOOR, "unavailable")
    await advance(hass, freezer, 120)
    assert not any(c.data["title"] == "Sensor unavailable" for c in calls["notify"])
    await set_state(hass, DOOR, "off")
    await _arm(hass)
    # a short drop-out is not reported
    await set_state(hass, WINDOW, "unavailable")
    await advance(hass, freezer, 30)
    await set_state(hass, WINDOW, "off")
    await advance(hass, freezer, 60)
    assert not any(c.data["title"] == "Sensor unavailable" for c in calls["notify"])
    # gone for longer: reported once
    await set_state(hass, WINDOW, "unavailable")
    await advance(hass, freezer, 180)
    reports = [c for c in calls["notify"] if c.data["title"] == "Sensor unavailable"]
    assert len(reports) == 1
    assert "Kitchen window" in reports[0].data["message"]
    assert _state(hass) == "armed_away"


async def test_sirens_and_sound_file(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    """Alarm sound without Alexa: siren entities and a file on the speakers."""
    freezer.move_to(START)
    media = "media-source://media_source/local/alarm.mp3"
    options = {
        "sirens": ["siren.hall"],
        "volume_players": ["media_player.kitchen"],
        "sound_media": media,
    }
    await setup_entry(hass, make_entry(**options))
    await _arm(hass)
    await set_state(hass, WINDOW, "on")
    assert calls["siren_on"][0].data["entity_id"] == ["siren.hall"]
    assert calls["play_media"][0].data["media_content_id"] == media
    assert calls["sound"] == []
    await _disarm(hass)
    assert calls["siren_off"][-1].data["entity_id"] == ["siren.hall"]


async def test_night_door_sirens_switch_off(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    await setup_entry(hass, make_entry(night_door_sensor=DOOR, night_sirens=["siren.hall"]))
    await hass.services.async_call("switch", "turn_on", {"entity_id": NIGHT}, blocking=True)
    await set_state(hass, DOOR, "on")
    assert calls["siren_on"][0].data["entity_id"] == ["siren.hall"]
    assert calls["siren_off"][0].data["entity_id"] == ["siren.hall"]


async def test_only_configured_entities(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    """Switches and buttons of functions that are not set up do not exist."""
    from homeassistant.helpers import entity_registry as er

    persons = [_person("p_a", "Alex", WIFI_A)]
    entry = make_entry(extra_subentries=persons, home_networks=[HOME])
    await setup_entry(hass, entry)
    registry = er.async_get(hass)
    assert hass.states.get(AUTO) is not None
    assert hass.states.get(ACK) is None
    assert registry.async_get("button.alarm_assistant_test_message").entity_category == "config"
    # the person is deleted: automatic arming and the presence sensor go away
    hass.config_entries.async_remove_subentry(entry, "p_a")
    await hass.async_block_till_done()
    assert registry.async_get(AUTO) is None
    assert registry.async_get("binary_sensor.alarm_assistant_alex_at_home") is None


async def test_remove_entry_deletes_issue(
    hass: HomeAssistant, base_states, calls, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to(START)
    entry = make_entry(turn_on_entities=["light.does_not_exist"])
    await setup_entry(hass, entry)
    assert ir.async_get(hass).async_get_issue(DOMAIN, "missing_entities") is not None
    await hass.config_entries.async_remove(entry.entry_id)
    await hass.async_block_till_done()
    assert ir.async_get(hass).async_get_issue(DOMAIN, "missing_entities") is None
