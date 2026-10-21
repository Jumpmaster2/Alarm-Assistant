"""WebSocket API of the panel."""

from __future__ import annotations

from homeassistant.core import HomeAssistant

from custom_components.alarm_assistant.logic.code import hash_code, verify_code

from .conftest import BALCONY, DOOR, make_entry, setup_entry


async def test_config_and_options(hass: HomeAssistant, base_states, hass_ws_client) -> None:
    entry = make_entry(code=hash_code("1234"))
    await setup_entry(hass, entry)
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "alarm_assistant/config"})
    msg = await client.receive_json()
    assert msg["success"]
    cfg = msg["result"]
    assert cfg["has_code"] is True
    assert "code" not in cfg["options"]
    assert cfg["options"]["entry_delay"] == 30
    assert cfg["entities"]["panel"] == "alarm_control_panel.alarm_assistant"
    assert len([s for s in cfg["subentries"] if s["type"] == "sensor"]) == 4

    await client.send_json_auto_id(
        {
            "type": "alarm_assistant/save_options",
            "options": {"entry_delay": "45", "turn_on_entities": ["light.hall", " "], "lock": DOOR},
        }
    )
    msg = await client.receive_json()
    assert msg["success"], msg
    assert entry.options["entry_delay"] == 45
    assert entry.options["turn_on_entities"] == ["light.hall"]
    assert verify_code("1234", entry.options["code"])

    # clearing an optional entity removes it, a cleared number falls back to the default
    await client.send_json_auto_id(
        {"type": "alarm_assistant/save_options", "options": {"lock": "", "entry_delay": None}}
    )
    msg = await client.receive_json()
    assert msg["success"]
    assert "lock" not in entry.options
    assert entry.options["entry_delay"] == 30

    await client.send_json_auto_id({"type": "alarm_assistant/save_options", "code": "99x"})
    msg = await client.receive_json()
    assert msg["error"]["message"] == "code_invalid"
    await client.send_json_auto_id({"type": "alarm_assistant/save_options", "code": "9999"})
    assert (await client.receive_json())["success"]
    assert verify_code("9999", entry.options["code"])
    await client.send_json_auto_id({"type": "alarm_assistant/save_options", "remove_code": True})
    assert (await client.receive_json())["success"]
    assert "code" not in entry.options

    await client.send_json_auto_id(
        {"type": "alarm_assistant/save_options", "options": {"not_an_option": 1}}
    )
    msg = await client.receive_json()
    assert not msg["success"]


async def test_subentries(hass: HomeAssistant, base_states, hass_ws_client) -> None:
    entry = make_entry(sensors=[])
    await setup_entry(hass, entry)
    client = await hass_ws_client(hass)

    await client.send_json_auto_id(
        {
            "type": "alarm_assistant/save_subentry",
            "subentry_type": "sensor",
            "title": "",
            "data": {"entity": BALCONY, "type": "window", "auto_bypass": True, "camera_preset": ""},
        }
    )
    msg = await client.receive_json()
    assert msg["success"], msg
    sub_id = msg["result"]["subentry_id"]
    sub = entry.subentries[sub_id]
    assert sub.title == "balcony door"
    assert "camera_preset" not in sub.data

    await client.send_json_auto_id(
        {
            "type": "alarm_assistant/save_subentry",
            "subentry_id": sub_id,
            "subentry_type": "sensor",
            "title": "Balcony",
            "data": {"entity": BALCONY, "type": "door"},
        }
    )
    assert (await client.receive_json())["success"]
    assert entry.subentries[sub_id].title == "Balcony"
    assert entry.subentries[sub_id].data["type"] == "door"

    await client.send_json_auto_id(
        {
            "type": "alarm_assistant/save_subentry",
            "subentry_type": "person",
            "title": "Alex",
            "data": {},
        }
    )
    msg = await client.receive_json()
    assert not msg["success"]
    assert msg["error"]["message"] == "entity_required"

    await client.send_json_auto_id(
        {"type": "alarm_assistant/delete_subentry", "subentry_id": sub_id}
    )
    assert (await client.receive_json())["success"]
    assert sub_id not in entry.subentries


async def test_test_arm_and_trigger(hass: HomeAssistant, base_states, hass_ws_client) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "alarm_assistant/test_trigger"})
    assert not (await client.receive_json())["success"]
    await client.send_json_auto_id(
        {"type": "alarm_assistant/test_arm", "disabled": ["lights", "push:notify.phone"]}
    )
    msg = await client.receive_json()
    assert msg["success"], msg
    assert entry.runtime_data.test == {"lights", "push:notify.phone"}
    await client.send_json_auto_id({"type": "alarm_assistant/test_trigger"})
    msg = await client.receive_json()
    assert msg["success"]
    assert msg["result"]["state"] == "triggered"
    await client.send_json_auto_id({"type": "alarm_assistant/config"})
    assert (await client.receive_json())["result"]["test_last"] == ["lights", "push:notify.phone"]


async def test_invalid_options_are_rejected(
    hass: HomeAssistant, base_states, hass_ws_client
) -> None:
    entry = make_entry()
    await setup_entry(hass, entry)
    client = await hass_ws_client(hass)
    cases = [
        ({"entry_delay": -50}, "entry_delay:out_of_range"),
        ({"alarm_volume": 7}, "alarm_volume:out_of_range"),
        ({"alarm_volume": "loud"}, "alarm_volume:not_a_number"),
        ({"lock_on_arm": "false"}, "lock_on_arm:not_bool"),
        ({"night_off_days": ["xyz"]}, "night_off_days:invalid_choice"),
        ({"presence_mode": "radar"}, "presence_mode:invalid_choice"),
        ({"night_off_time": "25:00"}, "night_off_time:invalid_time"),
        ({"turn_on_entities": "light.hall"}, "turn_on_entities:not_a_list"),
    ]
    for options, error in cases:
        await client.send_json_auto_id({"type": "alarm_assistant/save_options", "options": options})
        msg = await client.receive_json()
        assert not msg["success"], options
        assert msg["error"]["message"] == error
    assert entry.options["entry_delay"] == 30
    assert entry.options["alarm_volume"] == 0.51


async def test_invalid_subentries_are_rejected(
    hass: HomeAssistant, base_states, hass_ws_client
) -> None:
    entry = make_entry(sensors=[])
    await setup_entry(hass, entry)
    client = await hass_ws_client(hass)

    async def save(data: dict, title: str = "X", sub_type: str = "sensor") -> dict:
        await client.send_json_auto_id(
            {
                "type": "alarm_assistant/save_subentry",
                "subentry_type": sub_type,
                "title": title,
                "data": data,
            }
        )
        return await client.receive_json()

    msg = await save({"entity": DOOR, "type": "window", "arm_cover_position": "abc"})
    assert msg["error"]["message"] == "arm_cover_position:not_a_number"
    msg = await save({"entity": "not an entity", "type": "window"})
    assert msg["error"]["message"] == "entity:invalid_entity"
    msg = await save({"entity": DOOR, "type": "window", "foo": 1})
    assert msg["error"]["message"] == "foo:unknown_option"
    msg = await save(
        {"garage_panel": "alarm_control_panel.g", "garage_arm_delay": 99}, "G", "garage"
    )
    assert msg["error"]["message"] == "garage_arm_delay:out_of_range"
    assert entry.subentries == {}
    assert entry.state.value == "loaded"
    # the same entity twice
    assert (await save({"entity": DOOR, "type": "door"}))["success"]
    msg = await save({"entity": DOOR, "type": "window"}, "Y")
    assert msg["error"]["message"] == "entity:already_configured"
