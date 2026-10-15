"""WebSocket API for the panel: read the configuration, change options and sub items."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry, ConfigEntryState, ConfigSubentry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_CODE,
    CONF_ENTITY,
    CONF_GARAGE_PANEL,
    CONF_PERSON_WIFI,
    CONF_TYPE,
    DEFAULTS,
    DOMAIN,
    OPTIONAL_TEXT_KEYS,
    SUBENTRY_CAMERA,
    SUBENTRY_GARAGE,
    SUBENTRY_PERSON,
    SUBENTRY_SENSOR,
)
from .engine import hash_code
from .logic.state_machine import SENSOR_TYPES

DATA_WS = f"{DOMAIN}_ws_registered"
SUBENTRY_TYPES = (SUBENTRY_SENSOR, SUBENTRY_PERSON, SUBENTRY_CAMERA, SUBENTRY_GARAGE)

# entity keys of the integration (unique id suffix) for the panel
ENTITY_KEYS = {
    "panel": "alarm_control_panel",
    "auto_arm": "switch",
    "kids_home": "switch",
    "night_door": "switch",
    "live_mode": "switch",
    "garage_auto": "switch",
    "motion": "binary_sensor",
    "contacts_open": "binary_sensor",
    "motion_suppressed": "binary_sensor",
    "auto_arm_warning": "binary_sensor",
    "cause": "sensor",
    "last_triggered": "sensor",
    "call_acknowledge": "button",
    "test": "button",
}


@callback
def async_register_websocket(hass: HomeAssistant) -> None:
    if hass.data.get(DATA_WS):
        return
    hass.data[DATA_WS] = True
    websocket_api.async_register_command(hass, ws_config)
    websocket_api.async_register_command(hass, ws_save_options)
    websocket_api.async_register_command(hass, ws_save_subentry)
    websocket_api.async_register_command(hass, ws_delete_subentry)
    websocket_api.async_register_command(hass, ws_test_arm)
    websocket_api.async_register_command(hass, ws_test_trigger)


def _entry(hass: HomeAssistant) -> ConfigEntry | None:
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.state is ConfigEntryState.LOADED:
            return entry
    entries = hass.config_entries.async_entries(DOMAIN)
    return entries[0] if entries else None


def _coerce(key: str, value: Any) -> Any:
    """Bring a value from the panel into the type of the option."""
    default = DEFAULTS.get(key)
    if value is None or value == "":
        return None
    if isinstance(default, bool):
        return bool(value)
    if isinstance(default, int | float):
        number = float(value)
        return int(number) if isinstance(default, int) and number.is_integer() else number
    if isinstance(default, list):
        if not isinstance(value, list):
            raise vol.Invalid(f"{key} must be a list")
        return [str(v).strip() for v in value if str(v).strip()]
    return str(value).strip()


def config_payload(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    registry = er.async_get(hass)
    entities: dict[str, Any] = {}
    for key, domain in ENTITY_KEYS.items():
        if entity_id := registry.async_get_entity_id(domain, DOMAIN, f"{entry.entry_id}_{key}"):
            entities[key] = entity_id
    presence = {}
    for sub_id, sub in entry.subentries.items():
        if sub.subentry_type == SUBENTRY_PERSON and (
            entity_id := registry.async_get_entity_id("binary_sensor", DOMAIN, f"{sub_id}_presence")
        ):
            presence[sub_id] = entity_id
    devices = [
        {"id": device.id, "name": device.name_by_user or device.name or device.id}
        for device in dr.async_get(hass).devices.values()
        if any(ident[0] == "alexa_devices" for ident in device.identifiers)
    ]
    options = {k: v for k, v in entry.options.items() if k != CONF_CODE}
    engine = getattr(entry, "runtime_data", None)
    return {
        "entry_id": entry.entry_id,
        "options": {**DEFAULTS, **options},
        "has_code": bool(entry.options.get(CONF_CODE)),
        "subentries": [
            {"id": sub_id, "type": sub.subentry_type, "title": sub.title, "data": dict(sub.data)}
            for sub_id, sub in entry.subentries.items()
        ],
        "entities": entities,
        "presence": presence,
        "notify_services": sorted(
            f"notify.{name}" for name in hass.services.async_services_for_domain("notify")
        ),
        "alexa_devices": sorted(devices, key=lambda d: d["name"].lower()),
        "missing": list(getattr(engine, "missing", []) or []),
        "test_last": list(getattr(engine, "test_last", []) or []),
    }


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/config"})
@websocket_api.require_admin
@callback
def ws_config(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    entry = _entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "Alarm Assistant is not set up")
        return
    connection.send_result(msg["id"], config_payload(hass, entry))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save_options",
        vol.Optional("options", default={}): dict,
        vol.Optional("code"): str,
        vol.Optional("remove_code", default=False): bool,
    }
)
@websocket_api.require_admin
@callback
def ws_save_options(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    entry = _entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "Alarm Assistant is not set up")
        return
    options = dict(entry.options)
    try:
        for key, value in msg["options"].items():
            if key not in DEFAULTS and key not in OPTIONAL_TEXT_KEYS:
                raise vol.Invalid(f"unknown option {key}")
            coerced = _coerce(key, value)
            if coerced is None and key not in DEFAULTS:
                options.pop(key, None)
            elif coerced is None:
                options[key] = DEFAULTS[key]
            else:
                options[key] = coerced
    except (vol.Invalid, TypeError, ValueError) as err:
        connection.send_error(msg["id"], "invalid", str(err))
        return
    if msg["remove_code"]:
        options.pop(CONF_CODE, None)
    elif code := str(msg.get("code") or "").strip():
        options[CONF_CODE] = hash_code(code)
    hass.config_entries.async_update_entry(entry, options=options)
    connection.send_result(msg["id"], config_payload(hass, entry))


def _validate_subentry(subentry_type: str, title: str, data: dict[str, Any]) -> str | None:
    if subentry_type not in SUBENTRY_TYPES:
        return "unknown type"
    if not title.strip():
        return "name_required"
    if subentry_type == SUBENTRY_SENSOR:
        if not data.get(CONF_ENTITY):
            return "entity_required"
        if data.get(CONF_TYPE) not in SENSOR_TYPES:
            return "type_required"
    if subentry_type == SUBENTRY_PERSON and not data.get(CONF_PERSON_WIFI):
        return "entity_required"
    if subentry_type == SUBENTRY_GARAGE and not data.get(CONF_GARAGE_PANEL):
        return "entity_required"
    return None


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save_subentry",
        vol.Optional("subentry_id"): str,
        vol.Required("subentry_type"): str,
        vol.Required("title"): str,
        vol.Required("data"): dict,
    }
)
@websocket_api.require_admin
@callback
def ws_save_subentry(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    entry = _entry(hass)
    if entry is None:
        connection.send_error(msg["id"], "not_found", "Alarm Assistant is not set up")
        return
    data = {k: v for k, v in msg["data"].items() if v not in (None, "", [])}
    title = msg["title"].strip()
    if msg["subentry_type"] == SUBENTRY_SENSOR and not title and data.get(CONF_ENTITY):
        state = hass.states.get(str(data[CONF_ENTITY]))
        title = state.name if state else str(data[CONF_ENTITY])
    if error := _validate_subentry(msg["subentry_type"], title, data):
        connection.send_error(msg["id"], "invalid", error)
        return
    sub_id = msg.get("subentry_id")
    if sub_id:
        subentry = entry.subentries.get(sub_id)
        if subentry is None or subentry.subentry_type != msg["subentry_type"]:
            connection.send_error(msg["id"], "not_found", "sub item not found")
            return
        hass.config_entries.async_update_subentry(entry, subentry, data=data, title=title)
    else:
        subentry = ConfigSubentry(
            data=MappingProxyType(data),
            subentry_type=msg["subentry_type"],
            title=title,
            unique_id=None,
        )
        hass.config_entries.async_add_subentry(entry, subentry)
        sub_id = subentry.subentry_id
    connection.send_result(
        msg["id"], {"subentry_id": sub_id, "config": config_payload(hass, entry)}
    )


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/delete_subentry", vol.Required("subentry_id"): str}
)
@websocket_api.require_admin
@callback
def ws_delete_subentry(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    entry = _entry(hass)
    if entry is None or msg["subentry_id"] not in entry.subentries:
        connection.send_error(msg["id"], "not_found", "sub item not found")
        return
    hass.config_entries.async_remove_subentry(entry, msg["subentry_id"])
    connection.send_result(msg["id"], config_payload(hass, entry))


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/test_arm",
        vol.Optional("disabled", default=[]): [str],
    }
)
@websocket_api.require_admin
@callback
def ws_test_arm(hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict) -> None:
    """Arm as a test alarm with some reactions switched off."""
    entry = _entry(hass)
    engine = getattr(entry, "runtime_data", None) if entry else None
    if engine is None:
        connection.send_error(msg["id"], "not_found", "Alarm Assistant is not set up")
        return
    if engine.state != "disarmed":
        connection.send_error(msg["id"], "not_disarmed", "not_disarmed")
        return
    check = engine.arm_test(msg["disabled"])
    if not check.ok:
        names = ", ".join(engine.sensor_name(e) for e in check.blocking)
        connection.send_error(msg["id"], "arm_failed", names)
        return
    connection.send_result(msg["id"], {"state": engine.state})


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/test_trigger"})
@websocket_api.require_admin
@callback
def ws_test_trigger(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict
) -> None:
    """Trigger the running test alarm without a sensor."""
    entry = _entry(hass)
    engine = getattr(entry, "runtime_data", None) if entry else None
    if engine is None or not engine.simulate_trigger():
        connection.send_error(msg["id"], "not_test", "not_test")
        return
    connection.send_result(msg["id"], {"state": engine.state})
