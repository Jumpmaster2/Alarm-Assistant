"""Config flow, options flow and subentry flows."""

from __future__ import annotations

from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.alarm_assistant.const import (
    DOMAIN,
    SUBENTRY_CAMERA,
    SUBENTRY_GARAGE,
    SUBENTRY_PERSON,
    SUBENTRY_SENSOR,
)
from custom_components.alarm_assistant.logic.code import verify_code

from .conftest import AIRCON, BALCONY, DOOR, LOCK, make_entry, setup_entry

GENERAL = {
    "language": "auto",
    "notify_services": ["notify.phone"],
    "notify_alarm_services": [],
    "notify_admin_services": [],
}
ALARM = {
    "entry_delay": 30,
    "exit_delay": 0,
    "trigger_time": 1800,
    "disarm_after_trigger": False,
    "code_arm_required": False,
    "armed_on_entities": [],
}


async def test_user_flow(hass: HomeAssistant, base_states) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["step_id"] == "user"
    result = await hass.config_entries.flow.async_configure(result["flow_id"], GENERAL)
    assert result["step_id"] == "alarm"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**ALARM, "code": "4711", "code_confirm": "4712"}
    )
    assert result["errors"] == {"code": "code_mismatch"}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**ALARM, "code": "47a1", "code_confirm": "47a1"}
    )
    assert result["errors"] == {"code": "code_invalid"}
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {**ALARM, "code": "4711", "code_confirm": "4711"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    entry = result["result"]
    assert entry.options["notify_services"] == ["notify.phone"]
    assert entry.options["code"].startswith("pbkdf2_sha256$")
    assert verify_code("4711", entry.options["code"])
    assert entry.options["entry_delay"] == 30
    assert "next_flow" not in result


async def _options(hass: HomeAssistant, entry, step: str, data: dict) -> dict:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.MENU
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": step}
    )
    assert result["step_id"] == step
    result = await hass.config_entries.options.async_configure(result["flow_id"], data)
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    return result


async def test_options_code(hass: HomeAssistant, base_states) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "alarm"}
    )
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {**ALARM, "new_code": "12", "code_confirm": "12"}
    )
    assert result["errors"] == {"new_code": "code_invalid"}
    await _options(hass, entry, "alarm", {**ALARM, "new_code": "1234", "code_confirm": "1234"})
    assert verify_code("1234", entry.options["code"])
    # empty keeps the code
    await _options(hass, entry, "alarm", {**ALARM, "entry_delay": 45})
    assert verify_code("1234", entry.options["code"])
    assert entry.options["entry_delay"] == 45
    await _options(hass, entry, "alarm", {**ALARM, "remove_code": True})
    assert "code" not in entry.options


async def test_options_sections_and_clearing(hass: HomeAssistant, base_states) -> None:
    entry = make_entry(lock=LOCK)
    await setup_entry(hass, entry)
    await _options(
        hass,
        entry,
        "reactions",
        {
            "announce": {"announce_entities": [], "text_triggered": "Alarm!"},
            "siren": {
                "volume_players": [],
                "alarm_volume": 0.6,
                "reset_volume": 0.2,
                "reset_volume_after": 10,
                "sound_devices": [],
                "sound": "beep",
                "speak_services": [],
            },
            "actions": {"turn_on_entities": ["light.hall"], "close_covers": []},
        },
    )
    assert entry.options["text_triggered"] == "Alarm!"
    assert entry.options["alarm_volume"] == 0.6
    assert entry.options["turn_on_entities"] == ["light.hall"]
    # a cleared optional field is removed
    await _options(hass, entry, "lock", {"disarm_on_unlock": True, "lock_on_arm": False})
    assert "lock" not in entry.options
    assert entry.options["lock_on_arm"] is False


async def test_options_night_door(hass: HomeAssistant, base_states) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    await _options(
        hass,
        entry,
        "night_door",
        {
            "night_door_sensor": DOOR,
            "night_tag": "tag-1",
            "night_turn_on_entities": [],
            "night_volume_players": [],
            "night_sound_devices": [],
            "night_speak_services": [],
            "night_reset_volume_after": 5,
            "switch_off": {
                "night_off_time": "05:00:00",
                "night_off_days": ["mon", "fri"],
                "night_off_speak_services": [],
                "night_off_volume": 0.3,
            },
        },
    )
    assert entry.options["night_off_days"] == ["mon", "fri"]
    assert entry.options["night_tag"] == "tag-1"
    await hass.async_block_till_done()
    assert hass.states.get("switch.alarm_assistant_night_door_alarm") is not None


async def test_sensor_subentry(hass: HomeAssistant, base_states) -> None:
    entry = make_entry(sensors=[])
    await setup_entry(hass, entry)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_SENSOR), context={"source": SOURCE_USER}
    )
    assert result["step_id"] == "basics"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"entity": BALCONY, "type": "window"}
    )
    assert result["step_id"] == "behavior"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "use_entry_delay": False,
            "use_exit_delay": False,
            "auto_bypass": True,
            "allow_open": False,
            "only_when_unavailable": AIRCON,
            "arm_cover_position": 20,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    sub = next(iter(entry.subentries.values()))
    assert sub.title == "balcony door"  # name of the entity
    assert sub.data["only_when_unavailable"] == AIRCON
    # reconfigure: change the type, defaults of the new type are offered
    result = await entry.start_subentry_reconfigure_flow(hass, sub.subentry_id)
    assert result["step_id"] == "basics"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Balcony", "entity": BALCONY, "type": "door"}
    )
    assert result["step_id"] == "behavior"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "use_entry_delay": True,
            "use_exit_delay": True,
            "auto_bypass": False,
            "allow_open": False,
            "arm_cover_position": 20,
        },
    )
    assert result["type"] is FlowResultType.ABORT
    sub = entry.subentries[sub.subentry_id]
    assert sub.title == "Balcony"
    assert sub.data["type"] == "door"
    assert "only_when_unavailable" not in sub.data


async def test_garage_needs_wifi_sensors(hass: HomeAssistant, base_states) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_GARAGE), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "name": "Garage",
            "garage_panel": "alarm_control_panel.garage",
            "garage_networks": ["GarageNet"],
            "garage_arm_delay": 2,
            "garage_motion": [],
            "garage_tts_services": [],
            "garage_tts_repeat": 2,
        },
    )
    assert result["errors"] == {"garage_networks": "wifi_required"}


async def test_camera_and_garage_subentries(hass: HomeAssistant, base_states) -> None:
    entry = make_entry(wifi_sensors=["sensor.phone_a_wifi"])
    await setup_entry(hass, entry)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_CAMERA), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "name": " ",
            "privacy_delay": 2,
            "record_switches": [],
            "detect_switches": [],
            "person_push": True,
        },
    )
    assert result["errors"] == {"name": "name_required"}
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "name": "Living cam",
            "privacy_switch": "switch.cam_privacy",
            "ptz_home_preset": "Living",
            "privacy_delay": 2,
            "record_switches": [],
            "detect_switches": [],
            "person_push": True,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_GARAGE), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "name": "Garage",
            "garage_panel": "alarm_control_panel.garage",
            "garage_networks": ["GarageNet"],
            "garage_arm_delay": 2,
            "garage_motion": [],
            "garage_tts_services": [],
            "garage_tts_repeat": 2,
        },
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    garage = next(s for s in entry.subentries.values() if s.subentry_type == SUBENTRY_GARAGE)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_GARAGE),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": garage.subentry_id},
    )
    assert result["step_id"] == "reconfigure"
    await hass.async_block_till_done()
    assert hass.states.get("switch.alarm_assistant_garage_automatic") is not None
    assert hass.states.get("switch.alarm_assistant_camera_live_view") is not None


async def test_person_subentry(hass: HomeAssistant, base_states) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_PERSON), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Alex", "wifi_sensor": "sensor.phone_a_wifi"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()
    assert hass.states.get("binary_sensor.alarm_assistant_alex_at_home") is not None


async def test_sensor_subentry_rejects_duplicate(hass: HomeAssistant, base_states) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_SENSOR), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"entity": DOOR, "type": "door"}
    )
    assert result["errors"] == {"entity": "already_configured"}
    assert result["description_placeholders"]["other"] == "Front door"
    # changing the sensor itself keeps its entity
    sub_id = next(i for i, s in entry.subentries.items() if s.data["entity"] == DOOR)
    result = await entry.start_subentry_reconfigure_flow(hass, sub_id)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Door", "entity": DOOR, "type": "door"}
    )
    assert result["step_id"] == "behavior"
